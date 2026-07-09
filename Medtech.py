#Creating database and tables
import mysql.connector as mysql
mycon=mysql.connect(host='localhost',user='root',passwd='2210')
mycursor=mycon.cursor()
mycursor.execute('create database Medtech')
mycursor.execute('Use Medtech')
mycursor.execute('''CREATE TABLE Med_list ( med_code char(5) primary key,med_name char(15) not null,manufacturer char(25),
dosage_form char(10),category char(15),expire_date date,price float(5),medstock int(4))''')
print('Med_list table created')
mycursor.execute('''CREATE TABLE Pharma_devices (machine_id char(5) primary key,name char(25) not null,Warranty varchar(14),manufacturer char(25),
useins char(30),price float(6),stock int(4))''')
print('Pharma_devices table created')
mycursor.execute('''CREATE TABLE  Customer (cust_id CHAR(6) PRIMARY KEY,cust_name VARCHAR(50) NOT NULL,contact VARCHAR(10),
address VARCHAR(100))''')
print('Customer table created')
mycursor.execute('''CREATE TABLE Bill (bill_id CHAR(7) ,cust_id CHAR(6),item_name VARCHAR(50),quantity INT,
price FLOAT(7),total FLOAT(8),dt_purchase DATE,payment_mode VARCHAR(10),FOREIGN KEY (cust_id) REFERENCES Customer(cust_id))''')
print('Bill table created')
#Inserting into med_list
mycursor.execute("insert into med_list values ('M011','Dolo 650mg','Micro labs limited' ,'Tablets','Treat fever','2027-02-11',35,27)")
mycursor.execute("insert into med_list values ('M012','Aldigesic P','Alkem laboratories' ,'Tablets','Painkiller','2026-02-11',115,30)")
mycursor.execute("insert into med_list values ('M013','Benadryl','Jhonson Pvt limited' ,'Syrup','Cough and cold','2026-05-16',140,16)")
mycursor.execute("insert into med_list values ('M014','Optibex','Alkem Laboratories' ,'Eye drop','Dry fatigue eye','2026-03-26',90,12)")
mycursor.execute("insert into med_list values ('M015','HealthOK','Mankind Pharma ltd' ,'Tablets','Multivitamin','2026-01-22',220,23)")
mycursor.execute("insert into med_list values ('M016','Cipladine','Cipla labs' ,'Ointment','Antiseptic','2027-04-18',72,36)")
#Inserting into Pharma_devices
mycursor.execute("insert into Pharma_devices values ('P201','Blood Pressure Monitor' ,'3 months','Morepen Labs','Use twice a day',1247,7)")
mycursor.execute("insert into Pharma_devices values ('P202','Glucometer','4 months','Morepen Labs' ,'Use before and after meals',475,13)")
mycursor.execute("insert into Pharma_devices values ('P203','Perfecxa Nebulizer','1 year','Vertech health' ,'As directed by Pulmonologist',1790,6)")
mycursor.execute("insert into Pharma_devices values ('P204','Warm Bag','1 month','KVR Import house' ,null,470,19)")
mycursor.execute("insert into Pharma_devices values ('P205','Thermometer','2 months','DCG Labs' ,null,159,22)")
#Inserting into Customer
mycursor.execute("insert into customer values('C1001','Ruhi Chauhan','9975824322','C-19 greenville society')")
mycursor.execute("insert into customer values('C1002','Mohit Bansal','9843729188','D-56 Vikas Marg Delhi')")
mycursor.execute("insert into customer values('C1003','Madhur Singh','7281472947','A-1106 MIG Flats Delhi')")
#Inserting into Customer
mycursor.execute("insert into Bill values('B1001','C1001','Dolo 650mg',2,35,70,'2025-10-26','Cash')")
mycursor.execute("insert into Bill values('B1001','C1001','Glucometer',1,475,475,'2025-10-26','Cash')")
mycursor.execute("insert into Bill values('B1001','C1001','Cipladine',1,72,72,'2025-10-26','Cash')")
mycursor.execute("insert into Bill values('B1002','C1002','Aldigesic P',1,115,115,'2025-10-29','UPI')")
mycursor.execute("insert into Bill values('B1002','C1002','Optibex',1,90,90,'2025-10-29','UPI')")
mycursor.execute("insert into Bill values('B1003','C1003','Perfecxa Nebulizer',1,1790,1790,'2025-11-4','Card')")
mycursor.execute("insert into Bill values('B1003','C1003','Thermometer',1,159,159,'2025-11-4','Card')")
mycon.commit()
mycursor.close()
mycon.close()
