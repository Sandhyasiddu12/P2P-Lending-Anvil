from ._anvil_designer import dashboardTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ...bank_users.main_form import main_form_module
from ...bank_users.user_form import user_module

class dashboard(dashboardTemplate):
    def __init__(self, **properties):
        email = main_form_module.email
        self.init_components(**properties)
        self.email = main_form_module.email
        self.user_id=main_form_module.userId
        user_id = self.user_id

        # Fetch the user profile based on the current user's email
        user = anvil.users.get_user()
        # Check if a user is logged in
        if user:
            # Fetch the user profile record based on the current user's email
            user_profile = app_tables.fin_user_profile.get(email_user=user['email'])
            # Check if the user profile record is found
            if user_profile:
                # Access the user ID from the user profile record
                user_id = user_profile['customer_id']
                # Filter loan_details table based on the current user's ID
                try:
                    customer_loans = app_tables.fin_loan_details.search(borrower_customer_id=user_id)
                    print(len(customer_loans))
                except anvil.tables.NoSuchRow:
                    customer_loans = []  # Handle the case when no row is found
                    alert("No data found")

                # Check if the user has at least 3 loans
                if len(customer_loans) > 3:
                    self.extended_loans.visible = True
                else:
                    self.extended_loans.visible = False


    def home_main_form_link_click(self, **event_args):
        """This method is called when the link is clicked"""
        open_form("borrower_registration_form.dashboard")




    def button_3_click(self, **event_args):
        """This method is called when the button is clicked"""
        open_form('borrower_registration_form.dashboard.borrower_profile')

    def button_4_click(self, **event_args):
        """This method is called when the button is clicked"""
    
        email = main_form_module.email
    
        user_profile = app_tables.fin_user_profile.get(email_user=email)
    
        if user_profile:
            user_id = user_profile['customer_id']
    
            # Count the number of loans the user already has (based on specific patterns)
            try:
                existing_loans = app_tables.fin_loan_details.search(
                    borrower_customer_id=user_id,
                    loan_updated_status=q.any_of(
                        q.like('accept%'),
                        q.like('Approved%'),
                        q.like('approved%'),
                        q.like('under process%'),
                        q.like('foreclosure%'),
                        # q.like('close%'),
                        # q.like('Close%'),
                        # q.like('closed loans%'),
                        q.like('disbursed loan%'),
                        q.like('Disbursed loan%'),
                        q.like('Under Process%')
                    )
                )
                num_existing_loans = len(existing_loans)
                print(f"User ID: {user_id}, Existing Loans: {num_existing_loans}")
    
                # Check if the user has more than 5 loans
                if num_existing_loans >= 5:
                    alert("You already have 5 loans. Cannot open a new loan request.")
                else:
                    wallet_row = app_tables.fin_wallet.get(customer_id=user_id)
    
                    if wallet_row and wallet_row['wallet_id'] is not None:
                        open_form('borrower_registration_form.dashboard.new_loan_request')
                    else:
                        alert("Wallet not found. Please create a wallet.")
    
            except anvil.tables.TableError as e:
                # Check if the error message contains information about the non-existent row
                if "Row not found" in str(e):
                    # Handle the case when no row is found
                    alert("No data found.")
                else:
                    # Handle other table errors
                    alert("Error fetching existing loans.")

    def button_6_click(self, **event_args):
      open_form('borrower_registration_form.dashboard.view_loans')

    def outlined_button_1_click(self, **event_args):
      open_form('borrower_registration_form.dashboard.today_dues')

    def outlined_button_3_click(self, **event_args):
      open_form('borrower_registration_form.dashboard.application_tracker')

    def outlined_button_2_click(self, **event_args):
      open_form('borrower_registration_form.dashboard.foreclosure_request')

    def outlined_button_6_click(self, **event_args):
      open_form('borrower_registration_form.dashboard.dashboard_report_a_problem')

    def outlined_button_7_click(self, **event_args):
      open_form('borrower_registration_form.dashboard.view_transaction_history')

    def about_main_form_link_click(self, **event_args):
      open_form('borrower_registration_form.dashboard.dashboard_about')

    def notification_link_click(self, **event_args):
      open_form('borrower_registration_form.dashboard.notification')


  
    # this button is work for wallet 
    def wallet_dashboard_link_click(self, **event_args):
      open_form('wallet.wallet')



  

    def extended_loans_click(self, **event_args):
      open_form('borrower_registration_form.dashboard.extension_loan_request')

    def outlined_button_1_copy_3_click(self, **event_args):
      open_form('borrower_registration_form.dashboard.foreclosure_request')


    # this is for logout
    def logout_click(self, **event_args):
      alert("Logged out successfully")
      anvil.users.logout()
      open_form('bank_users.main_form')

    def borrower_dashboard_product_link_click(self, **event_args):
      """This method is called when the link is clicked"""
      pass

    def contact_main_form_link_click(self, **event_args):
      open_form('borrower_registration_form.dashboard.dashboard_contact')

    def Report_A_Problem_click(self, **event_args):
      open_form('b.d.d_r_a_p')
