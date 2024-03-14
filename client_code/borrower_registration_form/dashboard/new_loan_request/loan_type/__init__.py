import anvil.google.auth
import anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from anvil import open_form, alert
from .. import main_form_module as main_form_module
from ... import app_tables
from ._anvil_designer import loan_typeTemplate

class loan_type(loan_typeTemplate):
    def __init__(self, product_group, product_cat, product_name, max_amount_lb, product_description, entered_values=None, **properties):
        self.user_id = main_form_module.userId
        self.proctct_g = product_group
        self.prodct_cate = product_cat
        self.product_name = product_name
        self.credit_limt = max_amount_lb
        self.product_description = product_description  # Accept product_description
        self.init_components(**properties)
        
        # Initialize instance variables to store entered values
        self.entered_loan_amount = None
        self.entered_tenure = None
        self.entered_payment_type = None
        self.emi = None

        # Load previously entered values when the form is initialized
        self.load_entered_values(entered_values)

        user_request = app_tables.fin_product_details.get(product_name=self.product_name)
        if user_request:
            self.roi = user_request['roi']
            self.processing_fee = user_request['processing_fee']
            self.membership_type = user_request['membership_type']
            self.product_id = user_request['product_id']
            self.product_desc = user_request['product_discription']

            # Fetch emi_payment options from the database
            self.emi_payment_options = user_request['emi_payment']

            # Show/hide and adjust properties of buttons based on emi_payment options
            self.set_button_visibility()

    def load_entered_values(self, entered_values):
        if entered_values:
            # Load previously entered values into the form fields
            self.entered_loan_amount = entered_values.get('loan_amount', None)
            self.entered_tenure = entered_values.get('tenure', None)
            self.entered_payment_type = entered_values.get('payment_type', None)

            if self.entered_loan_amount is not None:
                self.loan_amount_tb.text = str(self.entered_loan_amount)
            if self.entered_tenure is not None:
                self.text_box_1.text = str(self.entered_tenure)
            if self.entered_payment_type is not None:
                # Set the selected button based on the stored value
                self.set_selected_payment_type(self.entered_payment_type)

    def set_selected_payment_type(self, payment_type):
        button_names = ["One Time", "Monthly", "Three Months", "Six Months"]
        for i, emi_option in enumerate(button_names):
            button = getattr(self, f'button_{i + 1}_1')
            if emi_option == payment_type:
                button.background = '#0a2346'
            else:
                button.background = '#939191'

    def set_button_visibility(self):
        available_options = ["One Time", "Monthly", "Three Months", "Six Months"]
        for i, emi_option in enumerate(available_options):
            button = getattr(self, f'button_{i + 1}_1')
            button.visible = emi_option in self.emi_payment_options
            button.text = emi_option

    def button_1_click(self, **event_args):
        open_form('borrower_registration_form.dashboard')

    def button_2_click(self, **event_args):
        open_form('borrower_registration_form.dashboard.new_loan_request')

    def button_3_click(self, **event_args):
        loan_amount = self.loan_amount_tb.text
        tenure = self.text_box_1.text
        payment_type = self.get_selected_payment_type()

        self.entered_loan_amount = loan_amount
        self.entered_tenure = tenure
        self.entered_payment_type = payment_type
        self.membership_type = self.membership_type

        if not any([self.label_22.text, self.label_23.text]):
            open_form('borrower_registration_form.dashboard.new_loan_request.check',
                      self.proctct_g, self.prodct_cate, self.product_name, str(loan_amount), tenure,
                      self.user_id, self.roi, self.processing_fee,
                      self.membership_type, self.product_id,self.product_desc,
                      self.Total_Repayment_Amount, self.credit_limt, self.entered_payment_type,
                      total_interest=self.label_30.text,
                      processing_fee_amount=self.label_32.text,
                      entered_values={
                          'loan_amount': self.entered_loan_amount,
                          'tenure': self.entered_tenure,
                          'payment_type': self.entered_payment_type
                      },
                      product_description=self.product_description,  # Pass product_description here
                      emi=self.emi)  # Pass monthly EMI here

    def fetch_product_data(self):
        return app_tables.fin_product_details.search(
            product_group=self.proctct_g,
            product_categories=self.prodct_cate
        )

    def get_min_max_amount(self):
        product_data = self.fetch_product_data()
        if product_data:
            min_amount = product_data[0]['min_amount']
            max_amount = product_data[0]['max_amount']
            return min_amount, max_amount
        return 0, 0

    def get_min_max_tenure(self):
        product_data = self.fetch_product_data()
        if product_data:
            min_tenure = product_data[0]['min_tenure']
            max_tenure = product_data[0]['max_tenure']
            return min_tenure, max_tenure
        return 0, 0

    def display_label_text(self, label, column_name):
        product_data = self.fetch_product_data()
        if product_data:
            label_text = [str(data[column_name]) for data in product_data]
            label.text = label_text[0] if label_text else None

    def label_11_show(self, **event_args):
        self.display_label_text(self.label_11, 'max_amount')

    def label_5_show(self, **event_args):
        self.display_label_text(self.label_5, 'min_amount')

    def label_13_show(self, **event_args):
        self.display_label_text(self.label_13, 'min_tenure')

    def label_15_show(self, **event_args):
        self.display_label_text(self.label_15, 'max_tenure')

    def label_21_show(self, **event_args):
        self.display_label_text(self.label_21, 'processing_fee')

    def label_7_show(self, **event_args):
        self.display_label_text(self.label_7, 'roi')

    def label_9_show(self, **event_args):
        self.display_label_text(self.label_9, 'foreclose_type')

    def label_18_show(self, **event_args):
        self.display_label_text(self.label_18, 'membership_type')

    def button_4_click(self, **event_args):
        loan_amount = self.loan_amount_tb.text
        tenure = self.text_box_1.text
        one_time = self.button_1_1.background == '#0a2346'
        monthly_emi = self.button_2_1.background == '#0a2346'
        three_months = self.button_3_1.background == '#0a2346'
        six_months = self.button_4_1.background == '#0a2346'

        if not loan_amount:
            self.label_22.text = "Please fill the loan amount"
            self.label_22.foreground = '#FF0000'
        elif not loan_amount.isdigit():
            self.label_22.text = "Please enter only numeric values (0-9) for loan amount"
            self.label_22.foreground = '#FF0000'
        else:
            min_amount, max_amount = self.get_min_max_amount()
            loan_amount = int(loan_amount)

            if min_amount <= loan_amount <= max_amount:
                self.label_22.text = ""
            else:
                self.label_22.text = f"Loan amount should be between {min_amount} and {max_amount}"
                self.label_22.foreground = '#FF0000'

        if not tenure:
            self.label_23.text = "Please select tenure"
            self.label_23.foreground = '#FF0000'
        elif not tenure.isdigit():
            self.label_23.text = "Please enter only numeric values (0-9) for tenure"
            self.label_23.foreground = '#FF0000'
        else:
            min_tenure, max_tenure = self.get_min_max_tenure()
            tenure = int(tenure)

            if min_tenure <= tenure <= max_tenure:
                self.label_23.text = ""
            else:
                self.label_23.text = f"Tenure should be between {min_tenure} and {max_tenure}"
                self.label_23.foreground = '#FF0000'

        if not (one_time or monthly_emi or three_months or six_months):
            self.label_24.text = "Please select the EMI Payment Type"
            self.label_24.foreground = '#FF0000'
        else:
            self.label_24.text = ""

            if not any([self.label_22.text, self.label_23.text, self.label_24.text]):
                self.grid_panel_2.visible = True
                self.button_2.visible = True
                self.button_3.visible = True
                self.button_5.visible = True
                self.button_4.visible = False

                self.label_28.text = f"₹ {loan_amount}"
                p = loan_amount
                t = tenure
                monthly_interest_rate = float(int(self.roi) / 100) / 12
                emi_denominator = ((1 + monthly_interest_rate) ** t) - 1
                emi_numerator = p * monthly_interest_rate * ((1 + monthly_interest_rate) ** t)
                Monthly_EMI = emi_numerator / emi_denominator
                self.label_36.text = f"₹ {Monthly_EMI:.2f}"
                interest_amount = Monthly_EMI * t - p
                self.label_30.text = f"₹ {interest_amount:.2f}"
                processing_fee_amount = (self.processing_fee / 100) * p
                self.label_32.text = f"₹ {processing_fee_amount:.2f}"
                self.Total_Repayment_Amount = Monthly_EMI * t + interest_amount + processing_fee_amount
                self.label_34.text = f"₹ {self.Total_Repayment_Amount:.2f}"

                # Pass monthly EMI value as well
                self.emi = Monthly_EMI

                self.loan_amount_tb.enabled = False
                self.text_box_1.enabled = False
                self.button_1_1.enabled = False
                self.button_2_1.enabled = False
                self.button_3_1.enabled = False
                self.button_4_1.enabled = False

    def button_5_click(self, **event_args):
        self.loan_amount_tb.enabled = True
        self.text_box_1.enabled = True
        self.button_1_1.enabled = True
        self.button_2_1.enabled = True
        self.button_3_1.enabled = True
        self.button_4_1.enabled = True
        self.grid_panel_2.visible = False
        self.button_2.visible = False
        self.button_3.visible = False
        self.button_5.visible = False
        self.button_4.visible = True

    def get_selected_payment_type(self):
        button_names = ["One Time", "Monthly", "Three Months", "Six Months"]
        for i, emi_option in enumerate(button_names):
            button = getattr(self, f'button_{i + 1}_1')
            if button.background == '#0a2346':
                return emi_option
        return None

    def button_1_1_click(self, **event_args):
        self.set_selected_payment_type("One Time")

    def button_2_1_click(self, **event_args):
        self.set_selected_payment_type("Monthly")

    def button_3_1_click(self, **event_args):
        self.set_selected_payment_type("Three Months")

    def button_4_1_click(self, **event_args):
        self.set_selected_payment_type("Six Months")

    def button_7_click(self, **event_args):
        """This method is called when the button is clicked"""
        pass

loan_type_1 = loan_type('product_group_value', 'product_cat_value', 'product_name', 'self.credit_limt', 'product_description_value')  # Pass product_description here

# Open the form
open_form(loan_type_1)
