# horus
Weapon against Osiris, ransomware.

This is an example script of how to use the gdrive API to revert an Osiris infestation. This is purely here as an example and will not run properly out of the box. You would need to register with google to get an API key before running this and even if you did that, this script has a very good chance of deleting data in your gdrive account if you run it as is without modification and testing. 

DO NOT RUN THIS SCRIPT UNLESS YOU KNOW WHAT YOU ARE DOING!!!!

But if you do know what you are doing, this is a good framework to get something working to get your files back. 

It works by looking for any files in your gdrive that have the word 'osiris' in the name.
For those files it tries to revert to the 2nd to last revision and rename the file to whatever the file was called in that 2nd to last revision. 

This means any files that this script decides to act on will delete the last revision of whatever file it deems infected. If it gets this wrong it could very well delete valid date. This script is very dangerous to run if you don't understand what it is doing.

YOU MUST DO YOU DUE DILIGENCE before allowing this script to actually take these actions. 

It makes some effort in backing up those files first to local disk but that might fail, but it still might continue and happily revert your perfectly good files without first downloading a backup. AGAIN, DO NOT RUN THIS UNLESS YOU KNOW WHAT YOU ARE DOING!!!

THIS IS PURELY AN EXAMPLE OF HOW TO WRITE A SCRIPT TO REVERT AN OSIRIS INFECTION OF A GDRIVE AND WILL NOT RUN OUT OF THE BOX!!!
