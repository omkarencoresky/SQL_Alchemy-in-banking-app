from sqlalchemy import create_engine, Column, Integer, String, DateTime,Date,Time,desc,ForeignKey
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, declarative_base,relationship
from typing import Optional, Tuple
import datetime
import hashlib
import random
import uuid
import os
import re
# from datetime import datetime


Base = declarative_base()


class User(Base):
    __tablename__ ='users'

    id = Column(Integer,primary_key=True)
    user_name  = Column(String(100), unique=True, nullable= False)
    password = Column(String(100), nullable=False)
    user_uuid = Column(String(100),unique=True,nullable=False)
    atm_number = Column(String(100),unique=True)
    atm_pin = Column(String(100))
    created_at = Column(DateTime, default=datetime.datetime.now)

    transactions = relationship("UserTransaction", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(username='{self.user_name}', user_uuid='{self.user_uuid}')>" 
    

class UserTransaction(Base):
    __tablename__ ='users_transactions'

    transaction_id = Column(Integer, primary_key=True, autoincrement=True)  
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # Foreign key referencing users table
    date = Column(Date, nullable=False)
    time = Column(Time,nullable=False)
    credit = Column(Integer,nullable=False, default=0)
    debit = Column(Integer,nullable=False, default=0)
    benefactor = Column(String,nullable=False, default=0)
    beneficiary = Column(String,nullable=False, default=0)
    total_balance = Column(Integer,nullable=False)

    user = relationship("User", back_populates="transactions")

class BankingFeatures:
    """
    This class is contains Banking related operations for customers
    """
    def __init__(self) -> None :
        """
        This constructor contains the creating engine and all variable for easy to access in all other methods.  
        """

        # ---------Create Database Engine----------

        self.engine = create_engine('mysql+mysqlconnector://omkar:root@localhost:3306/Banking_db')  # Create engine with driver of mysql-connector
        Base.metadata.create_all(self.engine)                                                       # Creating Database Tables
        session = sessionmaker(bind=self.engine)                                                    # Setting Up a Session
        self.session = session()                                                                    # Creating a Session Instance

        # ---------Variable----------

        self.total_balance: int = 0
        self.current_user_id: int = ""
        self.withdraw_amount: int = 0
        self.current_user_uuid: str = ""
        self.deposit_amount: int = 0

    def first_input_func(self) -> None :
        """
        This method handles the starting input for login and registration.
        """
        print("\nFor login enter =>'1'")
        print("For Registration enter => '2'")
        print("For Delete user enter => '3'")
        print("Transfer money ATM to account press => 4")
        print("For Exit enter => '5'")

        choice = input("Enter your choice here: ")

        if choice == '1':
            self.user_login()

        elif choice == '2':
            self.user_register()

        elif choice == '3':
            self.user_delete()

        elif choice == "4" :
            self.transfer_by_atm()

        elif choice == "5" :
            print("Exit........")
            return
        else:
            print("Enter your choice again")
            self.first_input_func()

    def input_func(self) -> None :
        """
        This method handle all the possible case related to input.  
        """
        main_choice = input("\nEnter input here for your operation: ")   

        if main_choice == "1" :
            self.withdraw()

        elif main_choice == "2" :
            self.deposit()

        elif main_choice == "3" :
            self.balance_inquiry()
            
        elif main_choice == "4" :
            self.transfer_to_account()

        elif main_choice == "5" :
            self.atm_transfer_atm()
            
        elif main_choice == "6" :
            self.transactions()

        elif main_choice == "7" :
            self.first_input_func()

        elif main_choice == "8" :
            self.session. expunge_all()
            print("Exit........")
            return
        else:
            print("\n'Invalid Input please input again'")
            self.input_func()
        return                    
    
    def user_register(self) -> None :
        """
        This method handle user registration process.  
        """

        print("\nEnter your details for registration")
        while True:
            user_name = input("""Enter you desired user name (without space): """)
            if 0 < len(user_name) < 25 and user_name.isalpha():
                user_password = input("Enter your password: ")
                if 0 < len(user_password) < 15:
                    hashed_password = hashlib.sha256(user_password.encode()).hexdigest()
                    user_name_uuid = str(uuid.uuid4())
                    print("\nDo you want to start the atm services")
                    print("For yes press 1 for no press any key......!")
                    choice = input("Enter your choice here: ")
                    if choice == "1":
                        random_atm_number = random.randint(100000000000,999999999999)
                        random_atm_pin = random.randint(1000,9999)
                        random_atm_number = str(random_atm_number)
                        atm_number = f"{random_atm_number[:4]}-{random_atm_number[4:8]}-{random_atm_number[8:12]}"
                        atm_pin = str(random_atm_pin)
                        hashed_atm_pin = hashlib.sha256(atm_pin.encode()).hexdigest()
                        print("Your user id: ", user_name_uuid)
                        print("Your ATM Number is :", atm_number)
                        print("Your ATM pin is :", atm_pin)
                        # print("Your hashed_atm_pin :", )
                    else:
                        atm_number = f"####-####-####"
                        hashed_atm_pin = "####"
                        print("Your user id: ", user_name_uuid)
                    print("-----------------Please Note this details -------------------")
                    new_user = User(
                        user_name = user_name,
                        password = hashed_password,
                        user_uuid = user_name_uuid,
                        atm_number = atm_number,
                        atm_pin = hashed_atm_pin
                    )
                        
                    session = self.session
                    try:
                        session.add(new_user)
                        session.commit()
                        first_entry = UserTransaction(
                            user_id = new_user.id,
                            date=datetime.datetime.now().date(),
                            time=datetime.datetime.now().time(),
                            credit = 0,
                            debit = 0,
                            transfer = 0,
                            total_balance = 0
                        )
                        session.add(first_entry)
                        session.commit()
                        print("User created successfully!")
                    except:
                        session.rollback()
                        print("Error: Username or UUID already exists. Please choose a different username.")
                    finally:
                        session.close()

                    self.first_input_func()
                    return
                else:
                    print("Password length maximum 10 character's")
            else:
                print("User name has only allow alphabets characters) (not allow numbers, special charatcers and blanks space")

    def user_login(self) -> None :
        """
        This method handle user login and open the statement file according to user's details.  
        """
        # Omkar password = 123 , sumit = 12, samrath = 1234 
        print("\nFor login to your account, please enter your details")
        user_uuid = input("Enter your user ID: ")
        session = self.session
        try:
            while True:
                user_id_confirmation = self.session.query(User).filter_by(user_uuid=user_uuid).first()
                if user_id_confirmation: 
                    password = input("Enter your password: ")
                    hashed_password = hashlib.sha256(password.encode()).hexdigest()
                    user_data = self.session.query(User).filter_by(password=hashed_password).first()
                    if user_data:                                                                               
                        print("\n----------------Login successful----------------")
                        print(f"Welcome to our services {user_data.user_name}")
                        transaction_details = self.session.query(UserTransaction).filter(UserTransaction.user_id == user_data.id).order_by(
                            desc(UserTransaction.time)).first()
                        self.current_user_uuid = user_data.user_uuid
                        self.total_balance = int(transaction_details.total_balance)
                        self.current_user_id = transaction_details.user_id
                        session.close()
                        self.menu()
                        self.input_func()
                        return
                    else:
                        print("Incorrect username or password. Please try again.")
                else:
                    print("Invalid user ID, please try again.")
                    user_uuid = input("Enter your user ID: ")
        finally:
            session.close()
        
    def withdraw(self) -> None :
        """
        This method handle withdraw related task and controle it.  
        """
        self.transfer_amount = input(f"Enter your amount for withdraw: ")
        if not self.transfer_amount.isdigit():
            print("Invalid Input, please enter amount again.")
            self.withdraw()
            return

        self.transfer_amount = int(self.transfer_amount)
        self.total_balance = int(self.total_balance)
        if int((self.transfer_amount)) > self.total_balance:
            print("\nYou have Insufficient balance please add balance in account first.")
            try:
                print("For continue press '1' and for exit press any key.")
                withdraw_choice = input("\nEnter your choice: ")
                while True:
                    if withdraw_choice == "1":
                        self.menu()
                        self.input_func()
                        return
                    else:
                        print ("--------------------Thanks for using our services--------------------") 
                        return 
            except:
                    self.input_func()
        elif self.transfer_amount == 0:
            print(f"Entered amount is {self.transfer_amount} so, Enter withdraw amount again")
            self.withdraw()
        else:
            self.sender_write_data()
            print("Withdrawal successful........!")
            print(f"Your current balance is: ₹{self.total_balance}")                                                                      
            self.menu()
            self.input_func()
            return
            
    def balance_inquiry(self) -> None :
        """
        This method handle balance related task and controle it.  
        """
        session = self.session
        try:
            user_data = self.session.query(User).filter(User.id == self.current_user_id).first()
            transaction_details = self.session.query(UserTransaction).filter(UserTransaction.user_id == user_data.id).order_by(
                                desc(UserTransaction.time)).first()
            self.total_balance = transaction_details.total_balance
            print(f"Your current balance is: ₹{self.total_balance}")

        finally:
            session.close()
        self.menu()
        self.input_func()
                               
    def deposit(self) -> None :
        """
        This method handle deposit related task and controle it.  
        """

        self.deposit_amount = input("Enter your desired deposit amount: ")

        if not self.deposit_amount.isdigit():
            print("Invalid input, please enter amount again")
            self.deposit()
            return

        self.deposit_amount = int(self.deposit_amount)
        self.total_balance = int(self.total_balance)

        if self.deposit_amount <= 0:
            print("Invalid amount, please enter positive amount")

        else:
            self.total_balance += self.deposit_amount
            print(f"Your current balance is: ₹{self.total_balance}")
            
            deposite_entry = UserTransaction(
                user_id = self.current_user_id,
                date=datetime.datetime.now(),
                time=datetime.datetime.now().time(),
                credit = self.deposit_amount,
                debit = 0,
                transfer = 0,
                total_balance = self.total_balance
            )
            session = self.session
            try:
                session.add(deposite_entry)
                session.commit()
            except:
                session.rollback()
            finally:
                session.close()
        self.menu()
        self.input_func()
        return

    def receiver_write_data(self,atm_number = None, pin = None, user_id = None) -> None:
        """
        This method contains the code to write or update the statement of recever's into statement file.  
        """
        # if user_id is not None:
        session = self.session
        try:
            if atm_number is not None:
                user_data = self.session.query(User).filter(User.atm_number == atm_number).first()
            else:
                user_data = self.session.query(User).filter(User.user_uuid == user_id).first()
            benefactor_details = self.session.query(User).filter(User.user_uuid == self.current_user_uuid).first()
            if user_data:
                transaction_details = self.session.query(UserTransaction).filter(UserTransaction.user_id == user_data.id).order_by(
                                desc(UserTransaction.time)).first()
                receiver_total_balance = int(transaction_details.total_balance)
                receiver_total_balance += self.transfer_amount
                receiver_entry = UserTransaction(
                    user_id = user_data.id,
                    date=datetime.datetime.now().date(),
                    time=datetime.datetime.now().time(),
                    credit = self.transfer_amount,
                    debit = 0,
                    benefactor = benefactor_details.user_name,
                    total_balance = receiver_total_balance
                )
                try:
                    session.add(receiver_entry)
                    session.commit()
                except:
                    session.rollback()
                finally:
                    session.close()
            else:
                print("Receiver id is not valid enter again.")
                self.transfer_to_account()
        finally:
            session.close()
        # else:
        #     print("Invalid receiver's id, enter again.")
        #     self.transfer_to_account()

    def sender_write_data(self, atm_number = None, pin = None, user_id = None) -> None:
        """
        This method contains the code to write or update the statement of sender's into statement file.  
        """
        try:
            sender_pin = input("Enter your pin here: ")
            hashed_pin = hashlib.sha256(sender_pin.encode()).hexdigest()
            session = self.session
            beneficiary_name_detail = self.session.query(User).filter(User.user_uuid == self.receiver_user_id).first()
            try:    
                user_data = self.session.query(User).filter(User.atm_pin == hashed_pin).first()
                if user_data:
                    self.total_balance -= self.transfer_amount
                    withdraw_entry = UserTransaction(
                            user_id = user_data.id,
                            date=datetime.datetime.now(),
                            time=datetime.datetime.now().time(),
                            credit = 0,
                            debit = self.transfer_amount,
                            beneficiary = beneficiary_name_detail.user_name,
                            total_balance = self.total_balance
                        )
                    session.add(withdraw_entry)
                    session.commit()
                        
                else:
                    self.sender_write_data()
            finally:
                session.close()
        except FileNotFoundError:
            print("Sender file not found.")
            self.input_func()

    def input_transfer_amount(self) -> None:
        """
        This method is use for take input of transfer ammount on different case.  
        """
        self.transfer_amount = input("Enter amount for transfer: ")
        if re.match(r'[1-9]\d*$',self.transfer_amount) and self.transfer_amount.isdigit():
            self.transfer_amount = int(self.transfer_amount)
        else:
            print("Invalid amount")
            self.input_transfer_amount()

    def input_receivers_id(self) -> str:
        """
        This method is use for take input of recever's id on different case.  
        """
        formats = r'[a-z0-9\-]+'
        self.receiver_user_id = input(f"Enter receiver's user id: ")
        if self.receiver_user_id != self.current_user_uuid:
            session = self.session
            try:
                user_data = self.session.query(User).filter(User.user_uuid == self.receiver_user_id).first()
                if user_data:
                    self.receiver_user_id = self.receiver_user_id
                else:
                    print("please enter the valid receiver's id.")
                    self.input_receivers_id()
            finally:
                session.close()
        else:
            print("This is your id, please enter the receiver's id.")
            self.input_receivers_id()

    def input_senders_id(self) -> None:
        """
        This method is use for take input of sender's id on different case.  
        """
        formats = r'[a-z0-9\-]+'
        self.senders_user_id = input(f"Enter senders's user id: ")
        self.senders_details=  self.file_details_open(user_id=self.senders_user_id)
        if self.senders_details is not None:
            if re.match(formats,self.senders_user_id) and self.senders_user_id == self.senders_details[1]:
                return
            else:
                print("Invalid Id")
                self.input_senders_id()
        else:
            print("Invalid Id")
            self.input_senders_id()

    def input_atm(self) -> str:
        """
        This method handles ATM number input and validation.
        """
        atm_pattern = r'^\d{4}-\d{4}-\d{4}$'
        while True:
            atm_number = input("Enter ATM Number: ")
            if re.match(atm_pattern, atm_number):
                session = self.session
                try:
                    receiver_atm_num = self.session.query(User).filter(User.atm_number == atm_number)
                    sender_atm_num = self.session.query(User).filter(User.user_uuid == self.current_user_uuid)
                    self.current_user_uuid
                    if receiver_atm_num is not None:
                        if receiver_atm_num != sender_atm_num:
                            return atm_number
                    print("Invalid ATM number or ATM number not found.")
                finally:
                    session.close()
            else:
                print("Invalid ATM number format.")
    
    def transfer_to_account(self) -> None :
        """
        This method is contain the code for transfer money to one account to other account with help of userid or name.
        """
        self.input_receivers_id()
        self.input_transfer_amount()
        self.receiver_write_data(user_id = self.receiver_user_id,)
        self.sender_write_data()
        print(f"Transfer amount {self.transfer_amount}₹ is successfully completed")
        print(f"Your current blance is : {self.total_balance}₹")
        self.menu()
        self.input_func()

        #-------------Working-------------

    def transfer_by_atm(self) -> None:
        """
        This method contains the code for transferring money by ATM number to another account with the help of user ID.
        """
        sender_atm_number = input('Enter Your atm number here: ')
        session = self.session
        sender_details = session.query(User).filter(User.atm_number == sender_atm_number).first()
        if sender_details:
            receiver_atm_number = input('Enter receiver\'s atm number here: ')
            receiver_details = session.query(User).filter(User.atm_number == receiver_atm_number).first()
            if receiver_details:
                self.input_transfer_amount()
                sender_pin = input("Enter your pin here: ")
                hashed_sender_pin = hashlib.sha256(sender_pin.encode()).hexdigest()
                if sender_details.atm_pin == hashed_sender_pin:
                    sender_transaction = session.query(UserTransaction).filter(UserTransaction.user_id == sender_details.id).order_by(desc(UserTransaction.time)).first()
                    sender_transaction.total_balance -= self.transfer_amount
                    sender_entry = UserTransaction(
                        user_id = sender_details.id,
                        date=datetime.datetime.now().date(),
                        time=datetime.datetime.now().time(),
                        credit=0,
                        debit=self.transfer_amount,
                        beneficiary=receiver_details.user_name,
                        total_balance=sender_transaction.total_balance
                    )

                    receiver_transaction = session.query(UserTransaction).filter(UserTransaction.user_id == receiver_details.id).order_by(desc(UserTransaction.time)).first()
                    receiver_transaction.total_balance += self.transfer_amount
                    receiver_entry = UserTransaction(
                        user_id=receiver_details.id,
                        date=datetime.datetime.now().date(),
                        time=datetime.datetime.now().time(),
                        credit=self.transfer_amount,
                        debit=0,
                        benefactor=sender_details.user_name,
                        total_balance=receiver_transaction.total_balance
                    )

                    session.add(sender_entry)
                    session.add(receiver_entry)
                    session.commit()

                    print(f"The amount {self.transfer_amount}₹ was successfully transferred to {receiver_details.user_name}")
                    print(f"Your current balance is: {sender_transaction.total_balance}₹")
                    self.first_input_func()
                else:
                    print("Entered password is wrong.")
                    self.transfer_by_atm()
            else:
                print("Receiver's ATM number is wrong.")
                self.transfer_by_atm()
        else:
            print("Sender's ATM number is wrong.")
            self.transfer_by_atm()
        session.close()

    def atm_transfer_atm(self) -> None :
        """
        This method is contain the code for transfer money by ATM number to ATM number.
        """
        print("Enter receiver ATM number")
        receivers_atm = self.input_atm()
        session = self.session
        try:    
            receivers_atm_num = self.session.query(User).filter(User.atm_number == receivers_atm).first()
            current_user = self.session.query(User).filter(User.user_uuid == self.current_user_uuid).first()
            if receivers_atm_num:
                if receivers_atm_num.atm_number != current_user.atm_number:
                    self.input_transfer_amount()
                    self.sender_write_data()
                    self.receiver_write_data(atm_number = receivers_atm)
                    self.menu() 
                    self.input_func()
                else:
                    print("This is your ATM number , enter receivers ATM number")
                    self.atm_transfer_atm()
            else:
                print("Envalid ATM number ,enter details again")
                self.atm_transfer_atm()
        finally:
            session.close()
            print(f"Transfer amount {self.transfer_amount}₹ is successfully completed")
            print(f"Your current blance is : {self.total_balance}₹")
            self.menu() 
            self.input_func()
            
    def user_delete(self) -> None :
        """
        This method is contains the code for delete the user's file and entry into the file_details file.
        """
        user_uuid = input("Enter your user id here: ")
        session =self.session
        try:
            user_uuid_confirm = self.session.query(User).filter(User.user_uuid == user_uuid).first()
            if user_uuid_confirm:
                password = input("Enter your password here: ")
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                if user_uuid_confirm.password == hashed_password:
                    try:
                        session.delete(user_uuid_confirm)
                        session.commit()
                        self.first_input_func()
                    finally:
                        session.close()
                    print("/nYour account delete successfully....!")
                    self.user_delete()
                else:
                    print("Wrong password entered")
                    self.user_delete()
            else:
                print("Wrong user_id entered")
                self.user_delete()
        except Exception as e:
            print(e)
        finally:
            session.close()

    def transactions(self) -> None :
        """
        This file contain the code for show the whole bank statement of a user.
        """
        session = self.session
        statement_format = "{:<20} {:<20} {:<20} {:<20} {:<20} {:<20} \n"
        print(statement_format.format("Date", "Time", "Credit", "Debit", "Transfer", "Balance", "ID"))
        statement = self.session.query(UserTransaction).all()  
        for transaction in statement:
            if transaction.user_id == self.current_user_id:
                print(statement_format.format(
                    transaction.date.strftime("%Y-%m-%d"),
                    transaction.time.strftime("%H:%M:%S"),
                    transaction.credit,
                    transaction.debit,
                    transaction.transfer,
                    transaction.total_balance,
                ))
        session.close()
        self.menu()
        self.input_func()

    def menu(self) -> None :
        """
        This method is contains Menu details. 
        """
        print("\nWithdrawal press => 1")
        print("Deposit press => 2") 
        print("Balance Inquiry press => 3")
        print("Transfer to account press => 4")
        print("ATM to ATM => 5")
        print("Account Statement press => 6")
        print("Home page press => 7")
        print("Exit press => 8")
            


#--------------------------------------- Creating instance -----------------------------------------------
if __name__ == "__main__":
    obj = BankingFeatures()
    obj.first_input_func()

    