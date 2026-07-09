import mysql.connector as mysql
from datetime import datetime
from tabulate import tabulate

mycon=mysql.connect(host='localhost',user='root',passwd='2210',database='medtech')
mycursor=mycon.cursor()

# Table 1 med_list
def add_med():
    print('------------------------Welcome------------------')
    code=input('Enter the Medicine code: ')
    name=input('Enter medicine name: ')
    mnfcr=input("Enter the Manufacturer's name: ")
    dsgeform=input('Enter dosage form: ')
    category=input('enter the category of medicine: ')
    expire=input('Enter the expiration date(YYYY-MM-DD): ')
    price=int(input('Enter the Medicines price: '))
    stock=int(input('Enter the current stock available: '))
    data=(code,name,mnfcr,dsgeform,category,expire,price,stock)
    mycursor.execute('insert into med_list values (%s,%s,%s,%s,%s,%s,%s,%s)',data)
    mycon.commit()

def search_med():
    wish='yes'
    while wish.lower()=='yes':
        print('1.Search details of medicine')
        print('2.Search current stock of medicine')
        print('3.Search using expiration date')
        ch=int(input('enter your choice:'))
        if ch==1:
            print('------------Medicine details------------')
            print('1.Use medicine code')
            print('2.Use medicine name')
            print('3.Use manufacturer name')
            print('4.Use category of the medicine')
            ch1=int(input('Enter the mode of search: '))
            if ch1==1:
                code=input('Enter medicine code: ')
                data=(code,)
                query='Select * from med_list where med_code=%s'
                mycursor.execute(query,data)
                for (code,name,manf,dsgform,category,expiry,price,stock) in mycursor:
                    print('Code:',code)
                    print('Name:',name)
                    print('Maunufacturer:',manf)
                    print('Dosage form:',dsgform)
                    print('Category:',category)
                    print('Expiration date:',expiry)
                    print('Price:',price)
                    print('Stock:',stock)
                    print('-'*40)
                    break
                else:
                    print('Code does not exist')
            elif ch1==2:
                name=input('Enter medicine name: ')
                data=(name,)
                query='Select * from med_list where med_name=%s'
                mycursor.execute(query,data)
                for (code,name,manf,dsgform,category,expiry,price,stock) in mycursor:
                    print('Code:',code)
                    print('Name:',name)
                    print('Maunufacturer:',manf)
                    print('Dosage form:',dsgform)
                    print('Category:',category)
                    print('Expiration date:',expiry)
                    print('Price:',price)
                    print('Stock:',stock)
                    print('-'*40)
                    break
                else:
                    print('Medicine is not available')
            elif ch1==3:
                mnf=input('Enter manufacturer name: ')
                data=(mnf,)
                query='Select * from med_list where manufacturer=%s'
                mycursor.execute(query,data)
                record=mycursor.fetchall()
                if record:
                    count=1
                    for (code,name,manf,dsgform,category,expiry,price,stock) in record :
                        print('Code:',code)
                        print('Name:',name)
                        print('Maunufacturer:',manf)
                        print('Dosage form:',dsgform)
                        print('Category:',category)
                        print('Expiration date:',expiry)
                        print('Price:',price)
                        print('Stock:',stock)
                        print('-'*40)
                        count+=1
                else:
                    print('Medicine from this manufacturer is not available')
                    print('-'*40)
            elif ch1==4:
                cat=input('Enter Category: ')
                data=(cat,)
                query='Select * from med_list where category=%s'
                mycursor.execute(query,data)
                record=mycursor.fetchall()
                if record:
                    count=1
                    for (code,name,manf,dsgform,category,expiry,price,stock) in record:
                        print('Code:',code)
                        print('Name:',name)
                        print('Maunufacturer:',manf)
                        print('Dosage form:',dsgform)
                        print('Category:',category)
                        print('Expiration date:',expiry)
                        print('Price:',price)
                        print('Stock:',stock)
                        count+=1
                        print('-'*40)
                else:
                    print('No medicine of this category available')
                    print('-'*40)
            else:
                print("Invalid choice! Please try again!\n")
                continue        
        elif ch==2:
            print('-------------Stock details--------------')
            stock=input('Enter Max stock amount: ')
            data=(stock,)
            query='Select med_code,med_name,medstock from med_list where medstock<=%s'
            mycursor.execute(query,data)
            record=mycursor.fetchall()
            if record:
                count=1
                for (code,name,stock) in record:
                    print('Code:',code)
                    print('Name:',name)
                    print('Stock amount:',stock)
                    print('-'*40)
                    count+=1
            else:
                print('No medicine is less in stock')
                print('-'*40)
        elif ch==3:
            date=input('Enter date upto which expiration needs to be checked(YYYY-MM-DD): ')
            data=(date,)
            mycursor.execute('Select med_code,med_name,expire_date from med_list where expire_date<=%s',data)
            record=mycursor.fetchall()
            if record:
                count=1
                for (code,name,expiry) in record:
                    print('Code:',code)
                    print('Name:',name)
                    print('Expiration Date:',expiry)
                    print('-'*40)
                    count+=1
            else:
                print('All medicines are up to date')
                print('-'*40)
        else:
            print("Invalid Choice please enter correct choice.\n")  
            continue      
        wish=input('Do you want to search again?: ')

def update_med():
    wish='yes'
    while wish.lower()=='yes':
        code=input('Enter medicine code for updation: ')
        c1=(code,)
        mycursor.execute('select med_code from med_list')
        check=mycursor.fetchall()
        for row in check:
            if row==c1:
                name=input('Do you wish to change the name of the medicine?(yes/-): ')
                if name=='yes':
                    medn=input('Enter new medicine name: ')
                    data=(medn,code)
                    mycursor.execute('Update med_list set med_name=%s where med_code=%s',data)
                manf=input('Do you wish to change the name of the manufacturer?(yes/-):')
                if manf=='yes':
                    mnf=input('Enter new manufacturer name: ')
                    data=(mnf,code)
                    mycursor.execute('Update med_list set manufacturer=%s where med_code=%s',data)
                dsg=input('Do you wish to change the form of dose?(yes/-): ')
                if dsg=='yes':
                    dose=input('Enter new form of dose: ')
                    data=(dose,code)
                    mycursor.execute('Update med_list set dosage_form=%s where med_code=%s',data)
                cate=input('Do you wish to change the category of the medicine?(yes/-):')
                if cate=='yes':
                    category=input('Enter new category of the medicine: ')
                    data=(category,code)
                    mycursor.execute('Update med_list set category=%s where med_code=%s',data)
                price=input('Do you wish to change the price of the medicine?(yes/-): ')
                if price=='yes':
                    Price=input('Enter new Price: ')
                    data=(Price,code)
                    mycursor.execute('Update med_list set price=%s where med_code=%s',data)
                stock=input('Do you wish to change the stock value?(yes/-): ')
                if stock=='yes':
                    stk=input('Enter new stockvalue: ')
                    data=(stk,code)
                    mycursor.execute('Update med_list set medstock=%s where med_code=%s',data)
                expiry=input('Do you wish to change the expiry date?(yes/-): ')
                if expiry=='yes':
                    expire=input('Enter new expiration date(YYYY-MM-DD): ')
                    data=(expire,code)
                    mycursor.execute('Update med_list set expire_date=%s where med_code=%s',data)
                mycon.commit()
                print('Updation successful')
                print('-'*40)
                break
        else:
            print('Code does not exist')
            print('-'*40)
        wish=input('Do you wish to update another record: ')
        
def delete_med():
    wish='yes'
    while wish.lower()=='yes':
        code=input('Enter the medicine code whose data has to be deleted: ')
        c1=(code,)
        mycursor.execute('select med_code from med_list')
        check=mycursor.fetchall()
        for row in check:
            if row==c1:
                data=(code,)
                query='Delete from med_list where med_code=%s'
                mycursor.execute(query,data)
                mycon.commit()
                print('Deletion Successful')
                print('-'*40)
                break
        else:
            print('Medicine Code does not exist')
            print('-'*40)
        wish=input('Do you wish to delete another record(yes/no): ')
        
# Table-2 Pharma_devices
        
def add_pharma_device():
    print('------------------------Welcome------------------')
    id=input('Enter pharma device id: ')
    name=input('Enter the device name: ')
    warranty= input('Enter the warranty of device: ')
    mfg=input("Enter the Manufacturer's name: ")
    useins=input("Enter the usage instructions of device: ")
    price=float(int(input('Enter the price of the device: ')))
    stock=int(input("Enter the stock size: "))
    data=(id,name,warranty,mfg,useins,price,stock)
    mycursor.execute('insert into pharma_devices values (%s,%s,%s,%s,%s,%s,%s)',data)
    print("Sucessfully inserted")
    mycon.commit()

def search_pharma_device():
    wish='yes'
    while wish.lower()=='yes':
        print('1.Search by details of devices')
        print('2.Search by price')
        ch=int(input('Enter your choice: '))
        if ch==1:
            print('------------PHARMA DEVICES------------')
            print('1. Use device name')
            print('2. Use manufacture name')
            print('3. Use stock value')
            ch1=int(input('Enter the mode of search: '))
            if ch1==1:
                name=input('Enter device name: ')
                data=(name,)
                query='Select * from pharma_devices where name=%s'
                mycursor.execute(query,data)
                print("------ Details of device is as follows--------")
                results = mycursor.fetchall()
                if results:
                    count = 1
                    for (id, name, warranty, mfg, usesins, price, stock) in results:
                        print(f"\n------ Record {count} ------")
                        print('Code:', id)
                        print('Name:', name)
                        print('Warranty:', warranty)
                        print('Manufacturer Name:', mfg)
                        print('Useins:', usesins)
                        print('Price:', price)
                        print('Stock:', stock)
                        print('-' * 40)
                        count += 1
                else:
                    print('Device is not available')
            elif ch1==2:
                name=input("Enter manufacturer name: ")
                data=(name,)
                query='Select * from pharma_devices where manufacturer=%s'
                mycursor.execute(query,data)
                print("------ Details of Manufacturer is as follows--------")
                results = mycursor.fetchall()
                if results:
                    count = 1
                    for (id, name, warranty, mfg, usesins, price, stock) in results:
                        print(f"\n------ Record {count} ------")
                        print('Code:', id)
                        print('Name:', name)
                        print('Warranty:', warranty)
                        print('Manufacturer Name:', mfg)
                        print('Useins:', usesins)
                        print('Price:', price)
                        print('Stock:', stock)
                        print('-' * 40)
                        count += 1                
                else:
                    print('Manufacturer name is not available')
            elif ch1==3:
                print("--Enter the stock range--:")
                start=float(input("Enter the starting stock range: "))
                end=float(input("Enter the ending stock range: "))
                print("------ Details of device by stock is as follows--------")
                query='Select *from pharma_devices where stock between %s and %s;'
                mycursor.execute(query,(start,end))
                results = mycursor.fetchall()
                if results:
                    count = 1
                    for (id, name, warranty, mfg, usesins, price, stock) in results:
                        print(f"\n------ Record {count} ------")
                        print('Code:', id)
                        print('Name:', name)
                        print('Warranty:', warranty)
                        print('Manufacturer Name:', mfg)
                        print('Useins:', usesins)
                        print('Price:', price)
                        print('Stock:', stock)
                        print('-' * 40)
                        count += 1
                else:
                    print('Stock range is not available')      
        
        elif ch==2:
            start=float(input("Enter the starting value of price: "))
            end=float(input("Enter the ending value of price: "))
            data=(start,end)
            query = "Select*from pharma_devices where price BETWEEN %s AND %s;"
            mycursor.execute(query,data)
            results = mycursor.fetchall()
            if results:
                count = 1
                for (id, name, warranty, mfg, usesins, price, stock) in results:
                    print(f"\n------ Record {count} ------")
                    print('Code:', id)
                    print('Name:', name)
                    print('Warranty:', warranty)
                    print('Manufacturer Name:', mfg)
                    print('Useins:', usesins)
                    print('Price:', price)
                    print('Stock:', stock)
                    print('-' * 40)
                    count += 1
            else:
                print('This price range is not available')
        wish=input('Do you want to search again(yes/no): ')


def update_pharma_devices():
    wish = 'yes'
    while wish.lower() == 'yes':
        code = input('Enter machine ID for updation: ')
        c1 = (code,)
        mycursor.execute('SELECT machine_id FROM Pharma_devices')
        check = mycursor.fetchall()

        for row in check:
            if row == c1:
                name = input('Do you wish to change the device name? ')
                if name.lower() == 'yes':
                    new_name = input('Enter new device name: ')
                    data = (new_name, code)
                    mycursor.execute('UPDATE Pharma_devices SET name=%s WHERE machine_id=%s', data)

                dwarranty = input('Do you wish to change the warranty duration of device? ')
                if dwarranty.lower() == 'yes':
                    new_warranty = input('Enter new warranty duration: ')
                    data = (new_warranty, code)
                    mycursor.execute('UPDATE Pharma_devices SET warranty=%s WHERE machine_id=%s', data)

                manufacturer = input('Do you wish to change the manufacturer name? ')
                if manufacturer.lower()=='yes':
                    new_manufacturer = input('Enter new manufacturer name: ')
                    data = (new_manufacturer, code)
                    mycursor.execute('UPDATE Pharma_devices SET manufacturer=%s WHERE machine_id=%s', data)

                useins = input('Do you wish to change the useins? ')
                if useins.lower() == 'yes':
                    new_useins = input('Enter new useins: ')
                    data = (new_useins, code)
                    mycursor.execute('UPDATE Pharma_devices SET useins=%s WHERE machine_id=%s', data)

                price = input('Do you wish to change the price? ')
                if price.lower() == 'yes':
                    new_price = float(input('Enter new price: '))
                    data = (new_price, code)
                    mycursor.execute('UPDATE Pharma_devices SET price=%s WHERE machine_id=%s', data)

                stock = input('Do you wish to change the stock value? ')
                if stock.lower()=='yes':
                    new_stock = int(input('Enter new stock value: '))
                    data = (new_stock, code)
                    mycursor.execute('UPDATE Pharma_devices SET stock=%s WHERE machine_id=%s', data)
                mycon.commit()
                print("-------------")
                print('Updation successful')
                print("-------------")
                break
        else:
            print('Machine ID does not exist.')
        wish=input('Do you wish to update another record: ')
        
def delete_pharma_device():
    wish='yes'
    while wish.lower()=='yes':
        code=input('Enter the medicine id whose data has to be deleted:')
        data=(code,)
        mycursor.execute('select machine_id from pharma_devices')
        check=mycursor.fetchall()
        for row in check:
            if row==data:
                c1=(code,)
                query='Delete from pharma_devices where machine_id=%s'
                mycursor.execute(query,c1)
                mycon.commit()
                print('Deletion Successful')
                break
        else:
            print('Machine Id does not exist')
        wish=input('Do you wish to delete another record?')

# Table-3 Customer

def add_record():
    print("\n--- Add Customer and Bill Details ---")


    cust_id = input("Enter Customer ID (e.g. C1001): ")
    cust_name = input("Enter Customer Name: ")
    contact = input("Enter Contact Number: ")
    address = input("Enter Address: ")

    query1 = "INSERT INTO Customer (cust_id, cust_name, contact, address) VALUES (%s, %s, %s, %s)"
    data1 = (cust_id, cust_name, contact, address)
    mycursor.execute(query1, data1)
    mycon.commit()
    print(" Customer record added successfully!")


    bill_id = input("\nEnter Bill ID: ")
    dt_purchase = input("Enter Date of Purchase (YYYY-MM-DD): ")
    payment_mode = input("Enter Payment Mode (Cash/Card/UPI): ")

    total_bill = 0

    while True:
        item_name = input("\nEnter Item Name: ")
        quantity = int(input("Enter Quantity: "))
        price = float(input("Enter Price per item: "))
        total = quantity * price
        total_bill += total

        query2 = '''INSERT INTO Bill 
                    (bill_id, cust_id, item_name, quantity, price, total, dt_purchase, payment_mode) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'''
        data2 = (bill_id, cust_id, item_name, quantity, price, total, dt_purchase, payment_mode)

        mycursor.execute(query2, data2)
        mycon.commit()

        print("Added",item_name,"to Bill", bill_id)

        more = input("Add another item to this bill? (yes/no: ")
        if more.lower() != 'yes':
            break

    print("\n Bill recorded successfully!")
    print("Total Bill Amount: Rs",total_bill,"\n")

def display_bill():
    bill_id = input("Enter Bill ID to view: ")

    query = '''
        SELECT cust_name, address, contact, 
               bill_id, dt_purchase, item_name, quantity, price, total, payment_mode
        FROM Bill 
        JOIN Customer  ON bill.cust_id = customer.cust_id
        WHERE bill.bill_id = %s
    '''
    mycursor.execute(query, (bill_id,))
    rows = mycursor.fetchall()

    if not rows:
        print("No bill found with that Bill ID.\n")
        return

    cust_name = rows[0][0]
    dt_purchase = rows[0][4].strftime("%Y-%m-%d")
    payment_mode = rows[0][9]

    items = []
    total_amount = 0
    for row in rows:
        items.append([row[5], row[6], row[7]])  # item_name, quantity, price
        total_amount += row[8]

    print("\n" + "="*60)
    print(" " * 20 + "BILL INVOICE")
    print("="*60)
    print("Customer Name:",cust_name,"Date of Purchase:",dt_purchase)
    print("Bill No:",bill_id)
    print("-"*60)
    print(tabulate(items, headers=["Medicine", "Quantity", "Price"], tablefmt="grid"))
    print("-"*60)
    print("Total Amount: ₹",total_amount)
    print("Mode of Payment:",payment_mode)
    print("="*60 + "\n")


#Main Program

print('----------------MEDTECH--------------------')

while True:
    print('1.Manage Medicines')
    print('2.Manage Healthcare devices')
    print('3.Manage Customers and Bills')
    print('4.Exit')
    ch1=int(input('Enter your choice: '))
    
    if ch1==1:
        while True:
            print('1.Add Medicine')
            print('2.Search Medicines')
            print('3.Update Medicines')
            print('4.Delete Medicines')
            print('5.Exit')
            ch2=int(input('Enter your choice: '))

            if ch2==1:
                add_med()
            elif ch2==2:
                search_med()
            elif ch2==3:
                update_med()
            elif ch2==4:
                delete_med()
            elif ch2==5:
                print('Returning to Main Menu,.....')
                break
            else:
                print('Invalid choice. Try again')
                
    elif ch1==2:
        while True:
            print('1.Add Healthcare Device')
            print('2.Search Devices')
            print('3.Update Devices')
            print('4.Delete Devices')
            print('5.Exit')
            ch2=int(input('Enter your choice: '))

            if ch2==1:
                add_pharma_device()
            elif ch2==2:
                search_pharma_device()
            elif ch2==3:
                update_pharma_devices()
            elif ch2==4:
                delete_pharma_device()
            elif ch2==5:
                print('Returning to Main Menu,.....')
                break
            else:
                print('Invalid choice. Try again')
                
    elif ch1==3:
        while True:
            print("1. Add Customer & Bill")
            print("2. Display Bill")
            print("3. Exit")
            choice = input("Enter your choice: ")
                
            if choice == '1':
                add_record()
            elif choice == '2':
                display_bill()
            elif choice == '3':
                print('Returning to Main Menu')
                break
            else:
                print("Invalid choice. Try again.\n")

    elif ch1==4:
        print('Goodbye')
        break
    else:
        print('Invalid choice.Try Again')
    
