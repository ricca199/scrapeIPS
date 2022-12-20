'''
Create Template email to send to potential clients
to make the offer to

Cold email template from PDF file
'''

To = "email address to use"
CC = "email address to put in CC"
text = """
<html>
<head></head>
<body>
<span style='font-size:11.0pt;font-family:"Calibri",sans-serif;color:#1F497D'>
    Hi,<br><br>Write below the email body.<br><br>Regards,<br><br>Cheers</p><br><b>
</span>
</body>
</html>
"""

def _emailer(text, subject,recipients,attachment,auto=True):
    import win32com.client as win32
    #Create outlook object
    outlook = win32.Dispatch('outlook.application')
    mail = outlook.CreateItem(0)
    mail.To = To
    mail.CC = CC
    mail.Subject = subject
    mail.HtmlBody = text
    mail.Attachments.Add(attachment)
    mail.send
    return 