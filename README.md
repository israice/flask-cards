## run
python run.py

---

# project log
## v001
- create flask with 2 html pages and google auth
- upload to github
## v002
- translate all code comments to english 
- SSE strwam data/auth_users.csv to templates\table.html
- adding Navbar with buttons
- allow table button only to admins from system_admin.csv 
## v003
- move all csv files to /data/ and update paths
- added AA_compaire_csv_files.py
- added AB_create_5_new_card_ids.py
- added AC_create_1_new_pack_id.py
- added A_run.py and 3 files as list
## v004
- add user to system_db next to pack
- create list of scripts for A_run_create_packs.py
- create list of scripts for B_run_send_packs_to_store.py
- create list of scripts for C_run_card_ownership.py
## v005
- create /core/ and fix paths for all files
## v006
- move all paths to .env and fix project paths
- redesighn login.html
## v007
- create add_card_owner.html
## v008
- create csv with CARD_AUTH keys
- change all existing sripts paths to .env
- create .env_EXAMPLE
## v009
- create AE_add_domain_to_system_card_url.py
- add /card/ to url inside core\data\system_card_auth.csv
- add card_id to core\data\system_card_auth.csv
## v010
- create AF_add_card_id_to_card_url.py
- create AG_add_card_id_to_image_file_name.py
## v011
- fix urls to show image id on html
## v012
- fix google button in add_card_owner.html
- show user cards list in profile page
- fix table.html
## v013
- run test.py when you login using add_card_owner.html
- create AH_create_qr_files.py
- change all script to be based on calmns index
## v014
- test scripts one by one make sure they works
- create generate_images.py
- fix module "create cards"
- fix run.py
- py files sorted by modules
## v015
- create button NEW PACK inside table.html
## v016
- create card system_card_stats.csv
- create system_card_coins.csv
- create system_full_db.csv
## v017
- half data checked and workin in system_full_db.csv
## v018
- 




## load last updates and replace existing local files
git fetch origin; git reset --hard origin/master; git clean -fd

## выбери хэш среди получиных последних 10
git log --oneline -n 10

## используй хэш для получения именно этого сахронения локально
git fetch origin; git checkout master; git reset --hard 1eaef8b;; git clean -fdx

## Quick github update
git add .
git commit -m "half data checked and workin in system_full_db.csv"
git push
