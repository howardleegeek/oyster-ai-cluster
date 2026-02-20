from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email
import logging
from typing import Union, Optional, List


logger = logging.getLogger("up")

MAIL_CONTENT = """
    Please use the following code as your confirmation: {}<br/>
    <br/>
"""


def send_mail(
        from_account: str,
        to_account: str,
        otp: str,
        api_key: str):
    message = Mail(
        from_email=Email(name="Universal Phone", email=from_account),
        to_emails=to_account,
        subject='Universal Phone Login Confirmation',
        html_content=MAIL_CONTENT.format(otp))
    try:
        logger.info("api key %s", api_key)
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        logger.info("sendmail response code %s", response.status_code)
        logger.info("sendmail response body %s", response.body)
        return "success"
    except Exception as err:
        logger.error("sendmail failed %s", err)
        return None


def send_mail_based_template(from_account, to_account, subject, content, api_key):
    message = Mail(
        from_email=Email(name="Universal Phone", email=from_account),
        to_emails=to_account,
        subject=subject,
        html_content=add_header_footer(content))
    try:
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        logger.info("sendmail based template response code %s", response.status_code)
        logger.info("sendmail based template response body %s", response.body)
        return "success"
    except Exception as err:
        logger.error("sendmail based template failed %s", err)
        return None


def add_header_footer(content: str):
    # TODO: change to real url on production
    header_img_url = "https://testing.universalphone.xyz/email_header.png"
    footer_img_url = "https://testing.universalphone.xyz/email_footer.png"
    
    return f"""
        <div style="text-align:center;">
            <img src="{header_img_url}" alt="Header Image" style="width:100%"/>
        </div>
        <div style="padding: 20px;">
            {content}
        </div>
        <div style="text-align:center;">
            <img src="{footer_img_url}" alt="Footer Image" style="width:100%"/>
        </div>
    """

def send_order_confirmed_mail(from_account: str, to_account: str, order_id: str, customer_name: str, shipping_address: str, blockchain_transaction_id: str, api_key: str):
    subject = "Order Confirmation – Address Lock-In Required for Shipping"
    content = f"""
        Dear {customer_name},<br/><br/>
        We’re excited to inform you that your Oyster Labs order has been successfully confirmed on the blockchain.<br/>
        To ensure a smooth delivery process, please sign in to your dashboard and lock in your shipping address.<br/><br/>
        <b>Order Confirmation Receipt</b><br/>
        Order ID: {order_id}<br/>
        Customer Name: {customer_name}<br/>
        Shipping Address: <br/>
        - {shipping_address} (Pending Confirmation)<br/>
        Blockchain Confirmation: <br/>
        - Transaction ID: {blockchain_transaction_id}<br/><br/>
        Thank you for your patience and for choosing Oyster Labs.<br/><br/>
        Best regards,<br/>Oyster Labs Team
    """
    return send_mail_based_template(from_account, to_account, subject, content, api_key)


def sendmail_denied(
        from_account: str, 
        api_key: str,
        to_account: str, 
        order_id: str, 
        tracking_number: Optional[str], 
        comments: Optional[str],
):
    subject = "Action Required: Shipping Issue with Your UBS1 Phone"
    tracking_number = tracking_number if tracking_number else "Not available"
    comments = comments if comments else "None"
    content = f"""
        Dear customer,<br/><br/>
        We regret to inform you that there has been an issue with the delivery of your UBS1 phone.<br/><br/>
        <b>Key Details:</b><br/>
        - Order ID: {order_id}<br/>
        - Tracking Number: {tracking_number}<br/>
        Feeback from shipping company: {comments}
        To resolve this and receive your phone, please:<br/>
        1. Log in to your Oyster Labs account at https://universalphone.xyz/signin.<br/>
        2. Go to "Orders".<br/>
        3. Select the UBS1 phone order.<br/>
        4. Follow the prompts to update and re-confirm your shipping information.<br/><br/>
        We apologize for the inconvenience and thank you for your cooperation.<br/><br/>
        Best regards,<br/>Oyster Labs Team
    """
    return send_mail_based_template(from_account, to_account, subject, content, api_key)


def sendmail_shipped(
        from_account: str, 
        api_key: str,
        to_account: str, 
        order_id: str, 
        tracking_number: Optional[str], 
        comments: Optional[str],
):
    subject = "UBS1 Phone Shipped – Important Update"
    tracking_number = tracking_number if tracking_number else "Not available"
    comments = comments if comments else "None"
    content = f"""
        Dear customer,<br/><br/>
        We’re excited to inform you that your UBS1 phone is on its way!<br/><br/>
        <b>Key Details:</b><br/>
        - Order ID: {order_id}<br/>
        - Tracking Number: {tracking_number}<br/>
        Feeback from shipping company: {comments}
        Depending on your current location, you can track your shipment at: https://www.17track.net/ or https://www.kuaidi100.com/<br/><br/>
        Please keep an eye on our website, your email and incoming phone calls for further updates.<br/><br/>
        Thank you for choosing Oyster Labs!<br/><br/>
        Best regards,<br/>Oyster Labs Team
    """
    return send_mail_based_template(from_account, to_account, subject, content, api_key)

def sendmail_delivered(
        from_account: str, 
        api_key: str,
        to_account: str, 
        order_id: str, 
        tracking_number: str, 
):
    subject = "UBS1 Phone Delivered"
    content = f"""
        Dear customer,<br/><br/>
        Your UBS1 phone is now delivered.<br/><br/>
        <b>Key Information:</b><br/>
        - Order ID: {order_id}<br/>
        -Tracking Number: {tracking_number}<br/>
        You can track your shipment at: https://www.17track.net/<br/><br/>
        Thank you for choosing Oyster Labs!<br/><br/>
        Best regards,<br/>Oyster Labs Team
    """
    return send_mail_based_template(
        from_account, 
        to_account, 
        subject, 
        content, 
        api_key)

def send_confirm_lock_address_mail(
        from_account: str, 
        to_account: str, order_id: str, customer_name: str, phone_number: str, shipping_address: str, order_status: str, api_key: str):
    subject = "Urgent: Confirm & Lock Your Shipping Address for UBS1 Delivery"
    content = f"""
        Dear {customer_name},<br/><br/>
        To ensure delivery of your UBS1 phone order, please review the following key details:<br/><br/>
        <b>Order Details:</b><br/>
        - Order ID: {order_id}<br/>
        - Order Status: {order_status}<br/>
        - Customer Name: {customer_name}<br/>
        - Phone Number: {phone_number}<br/>
        - Shipping Address: {shipping_address} (Pending Confirmation)<br/><br/>
        <b>We need your immediate action:</b><br/>
        1. <a href="https://universalphone.xyz/signin">Log in</a> to your Oyster Labs account.<br/>
        - Select the UBS1 phone order.<br/>
        - Use the local language for your address details.<br/>
        - Confirm and lock your address manually to ensure delivery. Failure to lock will prevent shipment.<br/><br/>
        2. Customs Clearance Code (For Specific Countries)<br/>
        - If you're in a country requiring a Personal Customs Clearance Code, enter it in your account under order details.<br/><br/>
        3. System Version Update<br/>
        - If your UBS1's system version is not 0924, update via OTA (Settings > About Phone > System Version > System Update).<br/><br/>
        Your cooperation ensures timely delivery and optimal device performance.<br/><br/>
        Thank you for choosing Oyster Labs!<br/><br/>
        Best regards,<br/>The Oyster Labs Team
    """
    return send_mail_based_template(from_account, to_account, subject, content, api_key)

