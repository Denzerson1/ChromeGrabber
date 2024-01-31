# Chrome Info Grabber by Denzersn
This is a Password, History and Card Stealer for the Chrome Browser.

This Software is only for academic use and should not be used for criminal circumstances.

1) History Stealer
First copies the History Database (AppData\Local\Google\Chrome\User Data\default\History), so the database can be read, while Google Chrome is running, as when it's running, the database is locked.
Afterwards a Sql Query to this SQLite Database, which gets the history, timestamp and title, is made, which we then write into a text file.

2) Password Stealer
Copies the needed Database (Login Data) aswell. The Passwords in this DB are encrypted using AES, which we decrypt by getting the masterkey, stored in Local State DB, which we then decrypt using base64 and win32crypt.

3) Card Stealer
Same Concept, Different SQLite request.
