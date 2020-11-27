
import smtplib
from email.mime.text import MIMEText
from email.header    import Header
with open('temp\\email_auth.txt', 'r') as fh:
    login, password = fh.read().split(';')

def sendEMail(msg, login, password):
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.login(login, password)
    message = msg.as_string()
    server.sendmail(login, login, message)
    server.quit()
html = '''<!DOCTYPE html>
<html>
<head>
<style>
th.column1 {
  text-align: left;
}
</style>
</head>
<body>
<table style="width:50%">
  <tr>
    <th class="column1">Товар</th>
    <th>Цена</th> 
    <th>Бонусы</th>
    <th>Процент скидки</th>
  </tr>

'''
html_end = '''
</table>
</body>
</html>'''
with open('temp\\result.csv', 'r') as fh:
    file = fh.readlines()
    for line in file[2:]:
        objects = line.split(';')
        html += f'''  <tr>
    <th class="column1">{objects[0]}</th>
    <th>{objects[1]}</th> 
    <th>{objects[2]}</th>
    <th>{objects[3]}</th>
  </tr>'''
html += html_end
msg = MIMEText(html, 'html', 'utf-8')
msg['Subject'] = Header('Dns-shop новые выгодные товары', 'utf-8')
msg['From'] = login
msg['to'] = login
sendEMail(msg, login, password)