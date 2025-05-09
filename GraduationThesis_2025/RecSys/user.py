class User:
    _counter = 0
    def __init__(self, role = 1):
        # 0: admin, 1: customer
        if role == 0: # --> admin
            self.id = f'A{User._counter}'
            self.password = 'P@ssw0rd'
        elif role == 1: # --> customer
            self.id = f'C{User._counter}'
            self.password = 'abc@123'
        User._counter += 1
        self.role = role

    @staticmethod
    def standardize_name(name):
        if not name:
            return name
        return name.lower().capitalize()
    
    def change_password(self, old_password, new_password):
        if self.password == old_password:
            self.password = new_password
            return True
        return False

class Admin(User):
    def __init__(self, lastname, firstname, email, last_login=None, activity_log=None):
        super().__init__(role=0)
        self.lastname = self.standardize(lastname)
        self.firstname = self.standardize(firstname)
        self.email = email
        self.last_login = last_login
        self.activity_log = activity_log if activity_log else []

    def __str__(self):
        return (f"[Admin] {self.firstname} {self.lastname} - ID: {self.id}, "
                f"Email: {self.email}, Last login: {self.last_login}, "
                f"Activities: {self.activity_log}")
    
    def add_user(self, user_list, user):
        user_list.append(user)

    def remove_user(self, user_list, user_id):
        for user in user_list:
            if user.id == user_id:
                user_list.remove(user)
                return True
        return False
    
    def log_activity(self, action):
        self.activity_log.append(f"{datetime.now()}: {action}")
        self.last_login = datetime.now()

class Customer(User):
    def __init__(self, lastname, firstname, phonenumber, address, email):
        super().__init__(role=1)
        self.lastname = self.standardize(lastname)
        self.firstname = self.standardize(firstname)
        self.phonenumber = phonenumber
        self.address = address
        self.email = email
        self.cart = []

    def __str__(self):
        return (f"[Customer] {self.firstname} {self.lastname} - ID: {self.id}, "
                f"Phone: {self.phonenumber}, Address: {self.address}, Email: {self.email}")
    
