# LibraryReissuer
  This is an application to reissue the books which have reached its due date.
  
## Features
* No Clicks required: Provide username(reg no.) and password in Terminal and get rid of unnecessary clicks.
* Auto-Reissue: Reissues book if it reached its due date.
* Reminder: If only one day is left then you get reminder to reissue/return your book immediately.
* Mailer: A mail using SMTP is sent if the books are reissued automaticaly or they can't be ressued online anymore.

## Setup
Clone or download the repo.
### To Clone:
`git clone https://github.com/aitoss/LibraryReissuer.git`

### Install MechanicalSoup
`pip3 install MechanicalSoup`

## Run
Enter Directory
`cd LibraryReissuer`
run python file
`python3 reissue.py`

## Scope
* to make chronjob so that python script runs automatically once a day.
