#This file does the same as tasks.py, but is used by teh pythonanywhere scheduled tasks rather than apschedular
from datetime import datetime

import xlsxwriter

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


from app import db, create_app
from app.models import Fish, Notification, Reminder, Stock

app = create_app()

def delete_old_notifications():
    with app.app_context():
        notifications = Notification.query.all()
        for notif in notifications:
            # how old is the notification in days
            notif_age = (datetime.today() - notif.time).days

            # if the notification is more than 100 dyas old, delete the notification
            if notif_age > 100:
                db.session.delete(notif)

        #commit the changes to the database
        db.session.commit()
    print("old notifs deleted ", str(datetime.now()))


def send_reminders():
    with app.app_context():
        reminders = Reminder.query.all()
        for reminder in reminders:
            if reminder.sent:
                continue
            if reminder.date is not None:
                if reminder.date <= datetime.today().date():
                    reminder.send_reminder()
        print("reminders sent ", str(datetime.now()))

def update_fish_months():
    with app.app_context():
        all_fish = Fish.query.filter(
            Fish.status != "Dead", Fish.birthday != None, Fish.system != "Old"
        ).all()

        for fish in all_fish:

            fish.months = fish.getMonths()



        db.session.commit()
        print("months updated "+str(datetime.now()))

def send_age_reminders():
    with app.app_context():
        all_fish = Fish.query.filter(Fish.status != "Dead", Fish.system != "Old").all()
        for fish in all_fish:

            if fish.months >= 23 and fish.age_reminder != "23 Months":
                fish.send_age_reminder(23)

            elif fish.months >= 17 and fish.age_reminder != "17 Months":
                fish.send_age_reminder(17)

            elif fish.months >= 11 and fish.age_reminder != "11 Months":
                fish.send_age_reminder(11)

            elif fish.months >= 5 and fish.age_reminder != "5 Months":
                fish.send_age_reminder(5)
        print("age reminders sent "+str(datetime.now()))


def update_stock_alive():
    with app.app_context():
        stocks = Stock.query.all()
        for stock in stocks:
            stock.has_alive_fish()
            if len(list(stock.fish)) < 1:
                    db.session.delete(stock)
        db.session.commit()

        print("Alive Stocks Updated "+str(datetime.now()))




def create_monthly_backup():
    today = datetime.today()
    if int(today.day) == 1:

        #create excel file and worksheet
        backup_path = '/home/FishFileBath/FishFile/Backups/'
        filename = f"FishFile_Backup_{str(today.date())}.xlsx"
        workbook = xlsxwriter.Workbook(backup_path+filename)
        worksheet = workbook.add_worksheet("Backup")

        #write data to worksheet
        with app.app_context():
            row = 0
            col = 0
            #write headings
            heading_format = workbook.add_format({'bold': True, 'font_color': 'white', 'bg_color': 'green', 'align': 'center', 'border':1})
            worksheet.set_column('A:X', 25)
            headings = ['ID', 'Tank #',  'Stock #', 'Birthday', 'Project Licence Allocated', 'User Code', 'Status',  'Date of Arrival', 'Protocol #', 'Comments', 'Mutant Gene', 'Transgenes', 'Allele', 'Type of cross', '# Unsexed fish', '# Females', '# Males', '# of carriers/licenced fish', '# Total',  'Mother ID','Mother Stock' ,'Father ID','Father Stock']
            for heading in headings:
                worksheet.write(row,col, heading, heading_format)
                col += 1

            row +=1


            #write fish data
            all_fish = Fish.query.order_by(Fish.stock_name.desc()).all()
            for fish in all_fish:
                col = 0
                worksheet.write(row,col,fish.fish_id)
                col += 1
                worksheet.write(row,col,fish.tank_id)
                col+= 1
                worksheet.write(row,col,fish.stock_name)
                col+=1
                if fish.old_birthday != None:
                    worksheet.write(row,col,str(fish.old_birthday))
                else:
                    worksheet.write(row,col,str(fish.birthday))
                col+=1
                if fish.old_license != None:
                    worksheet.write(row,col,fish.old_license)
                else:
                    worksheet.write(row,col,fish.project_license_holder.project_license)
                col+=1
                if fish.old_code != None:
                    worksheet.write(row,col,fish.old_code)
                else:
                    worksheet.write(row,col,fish.user_code.code)
                col+=1
                worksheet.write(row,col,fish.status)
                col+=1

                if fish.old_arrival != None:
                    worksheet.write(row,col,str(fish.old_arrival))
                elif fish.date_of_arrival != None:
                    worksheet.write(row,col,str(fish.date_of_arrival))
                col+=1
                if fish.protocol != None:
                    worksheet.write(row,col,fish.protocol)
                col+=1
                if fish.comments != None:
                    worksheet.write(row,col,fish.comments)
                col+=1
                if fish.mutant_gene != None:
                    worksheet.write(row,col,fish.mutant_gene)
                col+=1

                if fish.old_transgenes != None:
                    worksheet.write(row,col,fish.old_transgenes)
                elif len([gene.name for gene in fish.transgenes]) > 0:
                    worksheet.write(row,col,"\n".join([gene.name for gene in fish.transgenes]))
                col+=1
                if fish.old_allele != None:
                    worksheet.write(row,col,fish.old_allele)
                elif len([gene.name for gene in fish.alleles]) > 0:
                    worksheet.write(row,col,"\n".join([gene.name for gene in fish.alleles]))
                col+=1

                if fish.cross_type != None:
                    worksheet.write(row,col,fish.cross_type)
                col+=1

                if fish.unsexed != None:
                    worksheet.write(row,col,fish.unsexed)
                else:
                    worksheet.write(row,col,"0")
                col+=1

                if fish.females != None:
                    worksheet.write(row,col,fish.females)
                else:
                    worksheet.write(row,col,"0")
                col+=1
                if fish.males != None:
                    worksheet.write(row,col,fish.males)
                else:
                    worksheet.write(row,col,"0")
                col+=1
                if fish.carriers != None:
                    worksheet.write(row,col,fish.carriers)
                else:
                    worksheet.write(row,col,"0")
                col+=1
                if fish.total != None:
                    worksheet.write(row,col,fish.total)
                else:
                    worksheet.write(row,col,"0")
                col+=1

                if fish.old_mID != None:
                    worksheet.write(row,col,fish.old_mID)
                elif fish.mother != None:
                    worksheet.write(row,col,fish.mother.fish_ID)
                col+=1

                if fish.old_mStock != None:
                    worksheet.write(row,col,fish.old_mStock)
                elif fish.mother != None:
                    worksheet.write(row,col,fish.mother.stock)
                col+=1

                if fish.old_fID != None:
                    worksheet.write(row,col,fish.old_fID)
                elif fish.father != None:
                    worksheet.write(row,col,fish.father.fish_ID)
                col+=1

                if fish.old_fStock != None:
                    worksheet.write(row,col,fish.old_fStock)
                elif fish.father != None:
                    worksheet.write(row,col,fish.father.stock)
                col+=1


                row+=1

        #close the workseet
        workbook.close()
        print("Monthly Backup Created"+str(datetime.now()))



def update_stock_yearly():
    with app.app_context():
        today = datetime.today()
        if int(today.month) == 8 and int(today.day) == 18:
            stocks = Stock.query.all()
            for stock in stocks:

                stock.update_yearly_total()

            print("yearly update "+str(datetime.now()))



delete_old_notifications()
send_reminders()
update_fish_months()
send_age_reminders()
update_stock_alive()
create_monthly_backup()
update_stock_yearly()

print("all done")