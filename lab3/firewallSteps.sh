sudo apt install ufw; sudo ufw enable; sudo ufw allow 22/tcp
#Ensure this is a single command so that your SSH connection is not broken
#further testing demonstrated that enabling ufw did not break an established connection however further connection was not possible. Still recommend using this as a single line.
sudo ufw allow 65432
sudo ufw allow 65433
sudo ufw allow 65434
sudo ufw status verbose

#should output a match to what is below
#Status: active
#Logging: on (low)
#Default: deny (incoming), allow (outgoing), disabled (routed)
#New profiles: skip

#To                         Action      From
#--                         ------      ----
#22/tcp                     ALLOW IN    Anywhere                  
#65432                      ALLOW IN    Anywhere                  
#65433                      ALLOW IN    Anywhere                  
#65434                      ALLOW IN    Anywhere                  
#22/tcp (v6)                ALLOW IN    Anywhere (v6)             
#65432 (v6)                 ALLOW IN    Anywhere (v6)             
#65433 (v6)                 ALLOW IN    Anywhere (v6)             
#65434 (v6)                 ALLOW IN    Anywhere (v6)   
#This demonstrates a whitelist approach to incoming traffic wherein only approved ports are allowed to connect. All other inbound traffic is blocked
