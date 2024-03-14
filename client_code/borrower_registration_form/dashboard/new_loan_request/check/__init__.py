from datetime import datetime, timedelta
import anvil.server
from ... import app_tables
import anvil.tables as tables
from anvil import DataGrid, alert, open_form
from ._anvil_designer import checkTemplate
from .. import main_form_module as main_form_module

class check(checkTemplate):
    def __init__(self, product_group, product_cat, product_name, loan_amount, tenure_months, user_id, interest_rate, processing_fee,
                 membership_type, product_id, product_desc, total_repayment_amount, credit_limt, emi_payment_type, total_interest=None, processing_fee_amount=None, entered_values=None,
                 emi=None, **properties):
        # Initialize properties and data bindings
        self.product_group = product_group
        self.product_cat = product_cat
        self.product_name = product_name
        self.loan_amount = int(loan_amount)
        self.loan_amount_beginning_balance = self.loan_amount          
        self.tenure_months = int(tenure_months)
        self.user_id = user_id
        self.interest_rate = float(interest_rate)
        self.processing_fee = float(processing_fee)
        self.membership_type = membership_type
        self.product_id = product_id
        self.emi = round(emi, 2) if emi is not None else None  # Format emi to two decimal places
        
        
        self.total_interest = float(str(total_interest).replace('₹ ', '')) if total_interest is not None else 0
        self.processing_fee_amount = float(str(processing_fee_amount).replace('₹ ', '')) if processing_fee_amount is not None else 0
        self.total_repayment_amount = float(str(total_repayment_amount).replace('₹ ', '')) if total_repayment_amount is not None else 0
        self.total_repayment_amount = round(total_repayment_amount, 2)
        self.credit_limt = credit_limt
        self.entered_payment_type = emi_payment_type
        self.product_description = product_desc
        

        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Load previously entered values when the form is initialized
        self.load_entered_values(entered_values)

        # Calculate and display payment details based on the selected payment type
        self.calculate_and_display_payment_details()

    def load_entered_values(self, entered_values):
        if entered_values:
            # Load previously entered values into the form fields
            self.entered_loan_amount = entered_values.get('loan_amount', None)
            self.entered_tenure = entered_values.get('tenure', None)
            self.entered_payment_type = entered_values.get('payment_type', None)

    def submit_click(self, **event_args):
        # Call the server function to add loan details
        result = anvil.server.call('add_loan_details',
                                   self.loan_amount,
                                   self.tenure_months,
                                   self.user_id,
                                   self.interest_rate,
                                   self.total_repayment_amount,
                                   self.product_id,
                                   self.membership_type,
                                   self.credit_limt,
                                   self.product_name,
                                   self.entered_payment_type,
                                   self.processing_fee_amount,
                                   self.total_interest,
                                   self.product_description,
                                   self.emi)  # Pass product description here

        # Log the result for debugging
        print(result)

        # Show alert and navigate to the borrower dashboard
        alert("Request Submitted")
        open_form('borrower_registration_form.dashboard')

    def button_2_click(self, **event_args):
        open_form('borrower_registration_form.dashboard.new_loan_request.loan_type',
                  self.product_group,
                  self.product_cat,
                  self.product_name,
                  self.product_description,
                  self.credit_limt,
                  entered_values={
                      'loan_amount': self.entered_loan_amount,
                      'tenure': self.entered_tenure,
                      'payment_type': self.entered_payment_type
                  })

    def button_1_click(self, **event_args):
        open_form('borrower_registration_form.dashboard')

    def calculate_and_display_payment_details(self):
        # Calculate and display payment details based on the selected payment type
        if self.entered_payment_type == "One Time":
            self.display_one_time_payment_details()
        elif self.entered_payment_type == "Monthly":
            self.display_monthly_payment_details()
        elif self.entered_payment_type == "Three Months":
            self.display_three_month_payment_details(total_interest_amount=self.total_interest)
        elif self.entered_payment_type == "Six Months":
            self.display_six_month_payment_details(total_interest_amount=self.total_interest)

    def display_one_time_payment_details(self):
        # Display payment details for one-time payment
        total_repayment_amount = float(str(self.total_repayment_amount).replace('₹ ', ''))
        total_interest = float(str(self.total_interest).replace('₹ ', ''))
        processing_fee_amount = float(str(self.processing_fee_amount).replace('₹ ', ''))

        # Create a single row for one-time payment with the summary
        payment_details = [{
            'PaymentNumber': '1',
            'PaymentDate': 'Awaiting update',
            'ScheduledPayment': f"₹ {total_repayment_amount:.2f}",
            'Principal': f"₹ {self.loan_amount:.2f}",
            'Interest': f"₹ {total_interest:.2f}",
            'ProcessingFee': f"₹ {processing_fee_amount:.2f}",
            'BeginningBalance': f"₹ {total_repayment_amount:.2f}",
            'ExtraPayment': f"₹ 0.00",
            'TotalPayment': f"₹ {total_repayment_amount:.2f}",
            'EndingBalance': '₹ 0.00',
            'LoanAmountBeginningBalance': f"₹ {self.loan_amount:.2f}",
            'LoanAmountEndingBalance': f"₹ 0.00"
        }]

        # Set the Data Grid's items property to the single row
        self.repeating_panel_1.items = payment_details

    def display_monthly_payment_details(self):
        # Display payment details for monthly payment
        monthly_interest_rate = float(int(self.interest_rate) / 100) / 12
        emi_denominator = ((1 + monthly_interest_rate) ** self.tenure_months) - 1
        emi_numerator = self.loan_amount * monthly_interest_rate * ((1 + monthly_interest_rate) ** self.tenure_months)
        emi = emi_numerator / emi_denominator

        payment_details = self.calculate_payment_schedule(self.total_repayment_amount, emi, monthly_interest_rate)

        self.repeating_panel_1.items = payment_details

    def calculate_payment_schedule(self, total_repayment_amount, emi, monthly_interest_rate):
        payment_schedule = []
        processing_fee_per_month = (self.processing_fee / 100) * self.loan_amount / self.tenure_months

        beginning_balance = total_repayment_amount
        loan_amount_beginning_balance = self.loan_amount

        for month in range(1, self.tenure_months + 1):
            interest_amount = loan_amount_beginning_balance * monthly_interest_rate
            principal_amount = emi - interest_amount

            total_payment = emi + interest_amount + processing_fee_per_month
            loan_amount_ending_balance = loan_amount_beginning_balance - principal_amount

            payment_schedule.append({
                'PaymentNumber': month,
                'PaymentDate': "Awaiting update",
                'ScheduledPayment': f"₹ {emi:.2f}",
                'Principal': f"₹ {principal_amount:.2f}",
                'Interest': f"₹ {interest_amount:.2f}",
                'ProcessingFee': f"₹ {processing_fee_per_month:.2f}",
                'LoanAmountBeginningBalance': f"₹ {loan_amount_beginning_balance:.2f}",
                'LoanAmountEndingBalance': f"₹ {loan_amount_ending_balance:.2f}",
                'BeginningBalance': f"₹ {beginning_balance:.2f}",
                'ExtraPayment': "₹ 0.00",
                'TotalPayment': f"₹ {total_payment:.2f}",
                'EndingBalance': f"₹ {max(0,beginning_balance - total_payment):.2f}"
            })

            beginning_balance = beginning_balance - total_payment
            loan_amount_beginning_balance = loan_amount_ending_balance

        return payment_schedule

    def display_three_month_payment_details(self, total_interest_amount):
        # Display payment details for three-month payment
        annual_interest_rate = float(self.interest_rate)
        monthly_interest_rate = float(self.interest_rate) / 100 / 12
        emi_denominator = ((1 + monthly_interest_rate) ** self.tenure_months) - 1
        emi_numerator = self.loan_amount * monthly_interest_rate * ((1 + monthly_interest_rate) ** self.tenure_months)
        emi = emi_numerator / emi_denominator
        processing_fee_per_month = (self.processing_fee / 100) * self.loan_amount / self.tenure_months
        payment_schedule = self.calculate_three_month_payment_schedule(emi, monthly_interest_rate, processing_fee_per_month, total_interest_amount)
        self.repeating_panel_1.items = payment_schedule

    def calculate_interest_for_months(self, emi, loan_amount, monthly_interest_rate, start_month, end_month):
        total_interest = 0
    
        for month in range(start_month, end_month + 1):
            interest_amount = loan_amount * monthly_interest_rate
            total_interest += interest_amount
            loan_amount -= emi - interest_amount  # Update for the next month
    
        return total_interest
    
    def calculate_three_month_payment_schedule(self, emi, monthly_interest_rate, processing_fee_per_month, total_interest_amount):
        payment_schedule = []
        total_processing_fee = 0
    
        # Initialize beginning_balance and loan_amount_beginning_balance
        beginning_balance = self.total_repayment_amount
        loan_amount_beginning_balance = self.loan_amount
    
        for month in range(1, self.tenure_months + 1):
            interest_amount_row = loan_amount_beginning_balance * monthly_interest_rate
            principal_amount = emi - interest_amount_row
            loan_amount_ending_balance = loan_amount_beginning_balance - principal_amount
    
            total_processing_fee += processing_fee_per_month
    
            if month % 3 == 0 or month == self.tenure_months:
                remaining_months = self.tenure_months - month + 1
    
                if month % 3 == 0:
                    scheduled_payment = emi * 3
                elif month % 2 == 0:
                    scheduled_payment = emi * 2
                elif month % 1 == 0:
                    scheduled_payment = emi * 1
    
                if month % 3 == 0:
                    total_interest = self.calculate_interest_for_months(
                        emi, loan_amount_beginning_balance, monthly_interest_rate, month - 2, month)
                else:
                    total_interest = self.calculate_interest_for_months(
                        emi, loan_amount_beginning_balance, monthly_interest_rate, month - remaining_months, month)
    
                principal = scheduled_payment - total_interest
                total_payment = scheduled_payment + total_processing_fee + total_interest
    
                ending_balance = beginning_balance - total_payment
                loan_amount_ending_balance = loan_amount_beginning_balance - principal
    
                payment_schedule.append({
                    'PaymentNumber': len(payment_schedule) + 1,
                    'PaymentDate': "Awaiting update",
                    'BeginningBalance': f"₹ {beginning_balance:.2f}",
                    'ScheduledPayment': f"₹ {scheduled_payment:.2f}",
                    'ExtraPayment': "₹ 0.00",
                    'TotalPayment': f"₹ {total_payment:.2f}",
                    'Interest': f"₹ {total_interest:.2f}",
                    'Principal': f"₹ {principal:.2f}",
                    'ProcessingFee': f"₹ {total_processing_fee:.2f}",
                    'EndingBalance': f"₹ {max(0, ending_balance):.2f}",
                    'LoanAmountBeginningBalance': f"₹ {loan_amount_beginning_balance:.2f}",
                    'LoanAmountEndingBalance': f"₹ {loan_amount_ending_balance:.2f}"
                })
    
                total_processing_fee = 0
                beginning_balance = ending_balance
                loan_amount_beginning_balance = loan_amount_ending_balance
    
        return payment_schedule

    def display_six_month_payment_details(self, total_interest_amount):
        # Display payment details for six-month payment
        annual_interest_rate = float(self.interest_rate)
        monthly_interest_rate = float(self.interest_rate) / 100 / 12
        emi_denominator = ((1 + monthly_interest_rate) ** self.tenure_months) - 1
        emi_numerator = self.loan_amount * monthly_interest_rate * ((1 + monthly_interest_rate) ** self.tenure_months)
        emi = emi_numerator / emi_denominator
        processing_fee_per_month = (self.processing_fee / 100) * self.loan_amount / self.tenure_months
        payment_schedule = self.calculate_six_month_payment_schedule(emi, monthly_interest_rate, processing_fee_per_month, total_interest_amount)
        self.repeating_panel_1.items = payment_schedule
    
    def calculate_six_month_payment_schedule(self, emi, monthly_interest_rate, processing_fee_per_month, total_interest_amount):
        payment_schedule = []
        total_processing_fee = 0
    
        # Initialize beginning_balance and loan_amount_beginning_balance
        beginning_balance = self.total_repayment_amount
        loan_amount_beginning_balance = self.loan_amount
    
        for month in range(1, self.tenure_months + 1):
            interest_amount_row = loan_amount_beginning_balance * monthly_interest_rate
            principal_amount = emi - interest_amount_row
            loan_amount_ending_balance = loan_amount_beginning_balance - principal_amount
    
            total_processing_fee += processing_fee_per_month
    
            if month % 6 == 0 or month == self.tenure_months:
                remaining_months = self.tenure_months - month + 1
    
                if month % 6 == 0:
                    scheduled_payment = emi * 6
                elif month % 5 == 0:
                    scheduled_payment = emi * 5
                elif month % 4 == 0:
                    scheduled_payment = emi * 4
                elif month % 3 == 0:
                    scheduled_payment = emi * 3
                elif month % 2 == 0:
                    scheduled_payment = emi * 2
                elif month % 1 == 0:
                    scheduled_payment = emi * 1
    
                if month % 6 == 0:
                    total_interest = self.calculate_interest_for_months(
                        emi, loan_amount_beginning_balance, monthly_interest_rate, month - 5, month)
                else:
                    total_interest = self.calculate_interest_for_months(
                        emi, loan_amount_beginning_balance, monthly_interest_rate, month - remaining_months, month)
    
                principal = scheduled_payment - total_interest
                total_payment = scheduled_payment + total_processing_fee + total_interest
    
                ending_balance = beginning_balance - total_payment
                loan_amount_ending_balance = loan_amount_beginning_balance - principal
    
                payment_schedule.append({
                    'PaymentNumber': len(payment_schedule) + 1,
                    'PaymentDate': "Awaiting update",
                    'BeginningBalance': f"₹ {beginning_balance:.2f}",
                    'ScheduledPayment': f"₹ {scheduled_payment:.2f}",
                    'ExtraPayment': "₹ 0.00",
                    'TotalPayment': f"₹ {total_payment:.2f}",
                    'Interest': f"₹ {total_interest:.2f}",
                    'Principal': f"₹ {principal:.2f}",
                    'ProcessingFee': f"₹ {total_processing_fee:.2f}",
                    'EndingBalance': f"₹ {max(0, ending_balance):.2f}",
                    'LoanAmountBeginningBalance': f"₹ {loan_amount_beginning_balance:.2f}",
                    'LoanAmountEndingBalance': f"₹ {loan_amount_ending_balance:.2f}"
                })
    
                total_processing_fee = 0
                beginning_balance = ending_balance
                loan_amount_beginning_balance = loan_amount_ending_balance
    
        return payment_schedule
