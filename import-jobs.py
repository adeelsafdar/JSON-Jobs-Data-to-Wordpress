import MySQLdb
import requests
import urllib
from wordpress_xmlrpc import Client, WordPressPost, WordPressTerm
from wordpress_xmlrpc.compat import xmlrpc_client
from wordpress_xmlrpc.methods import media, posts, taxonomies
import json
from datetime import tzinfo, timedelta, datetime

# C:\Users\mugha\.windows-build-tools\python27\python.exe D:\wamp64\www\nokri\import-jobs.py

def dbconnect():
    try:
        db = MySQLdb.connect(
            host='localhost',
            user='root',
            passwd='',
            db='nokri-temp'
        )
    except Exception as e:
        sys.exit("Can't connect to database")
    return db

wp = Client('http://localhost:8080/nokri/xmlrpc.php', 'admin', '123456')

count = 1	
while 1 == 1:

	url = "https://www.mustakbil.com/ws/jobs/search/?page="+str(count)
	r=requests.get(url, headers={'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'})
	data = r.json()

	if data:
				
		for val in data['list']:
			
			temp_thumnail_id = 0
			
			id = val['id']
			employerId = val['employerId']
			title = val['title']
			type = val['type']
			shift = val['shift']
			experienceLevel = val['experienceLevel']
			salaryMin = val['salaryMin']
			salaryMax = val['salaryMax']
			currency = val['currency']
			description = val['description']
			cities = val['cities']
			country = val['country']
			postedOn = val['postedOn']

			if val['lastDate']:
				lastDate = datetime.strptime(val['lastDate'], '%b %d, %Y').strftime('%Y-%m-%d')
			else:
				lastDate = ''
			
			adType = val['adType']
			company = val['company']
			logo = val['logo']
			vacancies = val['vacancies']
			external = val['external']
			
			new_job = WordPressPost()
			new_job.title = title
			new_job.content = description
			new_job.post_type = 'job_listing'
			new_job.post_status = 'publish'
			
			new_job.id = wp.call(posts.NewPost(new_job))

			taxes = wp.call(taxonomies.GetTerms('job_listing_type'))
			is_present = 0
			post_category_id = 0

			for val in taxes:
				if str(val) == str(type):
					is_present = 1
					post_category_id = val.id
					break
				
			if is_present == 0:
				tag = WordPressTerm()
				tag.taxonomy = 'job_listing_type'
				tag.name = type
				post_category_id = wp.call(taxonomies.NewTerm(tag))

			category = wp.call(taxonomies.GetTerm('job_listing_type', post_category_id))
			post = wp.call(posts.GetPost(new_job.id))

			post.terms.append(category)
			wp.call(posts.EditPost(post.id, post))

			attachment_id = 0
			
			if logo:
			
				print "https://www.mustakbil.com"+str(logo)
				
				
				img_data = requests.get("https://www.mustakbil.com"+str(logo)).content
				with open('file01.jpg', 'wb') as handler:
					handler.write(img_data)
				
				
				filename = 'file01.jpg'

				data = {
						'name': 'picture.jpg',
						'type': 'image/jpeg',
				}

				with open(filename, 'rb') as img:
						data['bits'] = xmlrpc_client.Binary(img.read())

				response = wp.call(media.UploadFile(data))
				attachment_id = response['id']

			db = dbconnect()
			cursor = db.cursor()
			cursor.execute(""" 
			SELECT clk_adefd4319e_wp_posts.*, 
			       (SELECT clk_adefd4319e_wp_postmeta.meta_value 
			        FROM   clk_adefd4319e_wp_postmeta 
			        WHERE  clk_adefd4319e_wp_postmeta.meta_key = '_company_location' 
			               AND clk_adefd4319e_wp_postmeta.post_id = 
			                   clk_adefd4319e_wp_posts.ID) AS company_location,

			        (SELECT clk_adefd4319e_wp_postmeta.meta_value 
			        FROM   clk_adefd4319e_wp_postmeta 
			        WHERE  clk_adefd4319e_wp_postmeta.meta_key = '_company_email' 
			               AND clk_adefd4319e_wp_postmeta.post_id = 
			                   clk_adefd4319e_wp_posts.ID) AS company_email,

			        (SELECT clk_adefd4319e_wp_postmeta.meta_value 
			        FROM   clk_adefd4319e_wp_postmeta 
			        WHERE  clk_adefd4319e_wp_postmeta.meta_key = '_company_website' 
			               AND clk_adefd4319e_wp_postmeta.post_id = 
			                   clk_adefd4319e_wp_posts.ID) AS company_website

			                   
			FROM   clk_adefd4319e_wp_posts 
			WHERE  clk_adefd4319e_wp_posts.ID = (SELECT clk_adefd4319e_wp_postmeta.post_id 
			             FROM   clk_adefd4319e_wp_postmeta 
			             WHERE  clk_adefd4319e_wp_postmeta.meta_key = 'mustakbil_company_id' 
			                    AND clk_adefd4319e_wp_postmeta.meta_value = '"""+str(employerId)+"""') 
			 """)
			company_info = cursor.fetchone()
			if company_info:
				company_email = company_info[24]
				company_website = company_info[25]
			else:
				company_email = ''
				company_website = ''
			db = dbconnect()
			cursor = db.cursor()
			print """ INSERT INTO clk_adefd4319e_wp_postmeta (post_id,meta_key,meta_value) VALUES ('"""+new_job.id+"""','_filled','0'); """
			cursor.execute(""" INSERT INTO clk_adefd4319e_wp_postmeta (post_id,meta_key,meta_value) VALUES ('"""+new_job.id+"""','_filled','0') """)
			db.commit()
			cursor.close()

			cursor = db.cursor()
			print """ INSERT INTO clk_adefd4319e_wp_postmeta (post_id,meta_key,meta_value) VALUES ('"""+new_job.id+"""','_featured','0'); """
			cursor.execute(""" INSERT INTO clk_adefd4319e_wp_postmeta (post_id,meta_key,meta_value) VALUES ('"""+new_job.id+"""','_featured','0') """)
			db.commit()
			cursor.close()
			
			cursor = db.cursor()
			print """ INSERT INTO clk_adefd4319e_wp_postmeta (post_id,meta_key,meta_value) VALUES ('"""+new_job.id+"""','_edit_lock','1552747389:1'); """
			cursor.execute(""" INSERT INTO clk_adefd4319e_wp_postmeta (post_id,meta_key,meta_value) VALUES ('"""+new_job.id+"""','_edit_lock','1552747389:1') """)
			db.commit()
			cursor.close()
			
			cursor = db.cursor()
			print """ INSERT INTO clk_adefd4319e_wp_postmeta (post_id,meta_key,meta_value) VALUES ('"""+new_job.id+"""','_job_expires','"""+str(lastDate)+"""'); """
			cursor.execute(""" INSERT INTO clk_adefd4319e_wp_postmeta (post_id,meta_key,meta_value) VALUES ('"""+new_job.id+"""','_job_expires','"""+str(lastDate)+"""') """)
			db.commit()
			cursor.close()
			
			cursor = db.cursor()
			print """ INSERT INTO clk_adefd4319e_wp_postmeta (post_id,meta_key,meta_value) VALUES ('"""+new_job.id+"""','_edit_last','1'); """
			cursor.execute(""" INSERT INTO clk_adefd4319e_wp_postmeta (post_id,meta_key,meta_value) VALUES ('"""+new_job.id+"""','_edit_last','1') """)
			db.commit()
			cursor.close()
			
			cursor = db.cursor()
			print """ INSERT INTO clk_adefd4319e_wp_postmeta (post_id,meta_key,meta_value) VALUES ('"""+new_job.id+"""','_job_location','"""+str(cities)+"""'); """
			cursor.execute(""" INSERT INTO clk_adefd4319e_wp_postmeta (post_id,meta_key,meta_value) VALUES ('"""+new_job.id+"""','_job_location','"""+str(cities)+"""') """)
			db.commit()
			cursor.close()

			cursor = db.cursor()
			print """ INSERT INTO clk_adefd4319e_wp_postmeta (post_id,meta_key,meta_value) VALUES ('"""+new_job.id+"""','_application',''); """
			cursor.execute(""" INSERT INTO clk_adefd4319e_wp_postmeta (post_id,meta_key,meta_value) VALUES ('"""+new_job.id+"""','_application','"""+str(company_email)+"""') """)
			db.commit()
			cursor.close()
			
			cursor = db.cursor()
			print """ INSERT INTO clk_adefd4319e_wp_postmeta (post_id,meta_key,meta_value) VALUES ('"""+new_job.id+"""','_company_name','""" + str(company) + """'); """
			cursor.execute(""" INSERT INTO clk_adefd4319e_wp_postmeta (post_id,meta_key,meta_value) VALUES ('"""+new_job.id+"""','_company_name','""" + str(company) + """') """)
			db.commit()
			cursor.close()
			
			cursor = db.cursor()
			print """ INSERT INTO clk_adefd4319e_wp_postmeta (post_id,meta_key,meta_value) VALUES ('"""+new_job.id+"""','_company_website',''); """
			cursor.execute(""" INSERT INTO clk_adefd4319e_wp_postmeta (post_id,meta_key,meta_value) VALUES ('"""+new_job.id+"""','_company_website','"""+str(company_website)+"""') """)
			db.commit()
			cursor.close()
			
			cursor = db.cursor()
			print """ INSERT INTO clk_adefd4319e_wp_postmeta (post_id,meta_key,meta_value) VALUES ('"""+new_job.id+"""','_company_tagline',''); """
			cursor.execute(""" INSERT INTO clk_adefd4319e_wp_postmeta (post_id,meta_key,meta_value) VALUES ('"""+new_job.id+"""','_company_tagline','') """)
			db.commit()
			cursor.close()
			

			cursor = db.cursor()
			print """ INSERT INTO clk_adefd4319e_wp_postmeta (post_id,meta_key,meta_value) VALUES ('"""+new_job.id+"""','_company_twitter',''); """
			cursor.execute(""" INSERT INTO clk_adefd4319e_wp_postmeta (post_id,meta_key,meta_value) VALUES ('"""+new_job.id+"""','_company_twitter','') """)
			db.commit()
			cursor.close()

			cursor = db.cursor()
			print """ INSERT INTO clk_adefd4319e_wp_postmeta (post_id,meta_key,meta_value) VALUES ('"""+new_job.id+"""','_company_video',''); """
			cursor.execute(""" INSERT INTO clk_adefd4319e_wp_postmeta (post_id,meta_key,meta_value) VALUES ('"""+new_job.id+"""','_company_video','') """)
			db.commit()
			cursor.close()
			

			cursor = db.cursor()
			print """ INSERT INTO clk_adefd4319e_wp_postmeta (post_id,meta_key,meta_value) VALUES ('"""+new_job.id+"""','_thumbnail_id','"""+str(attachment_id)+"""'); """
			cursor.execute(""" INSERT INTO clk_adefd4319e_wp_postmeta (post_id,meta_key,meta_value) VALUES ('"""+new_job.id+"""','_thumbnail_id','"""+str(attachment_id)+"""') """)
			db.commit()
			cursor.close()
			

		count += 1
		
	else:
		break