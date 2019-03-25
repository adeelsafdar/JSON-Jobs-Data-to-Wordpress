import MySQLdb
import requests
import urllib
from wordpress_xmlrpc import Client, WordPressPost, WordPressTerm
from wordpress_xmlrpc.compat import xmlrpc_client
from wordpress_xmlrpc.methods import media, posts, taxonomies
import json

# C:\Users\mugha\.windows-build-tools\python27\python.exe D:\wamp64\www\nokri\import-companies.py

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

	url = "https://www.mustakbil.com/ws/companies/search/?page="+str(count)
	r=requests.get(url, headers={'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'})
	data = r.json()

	if data:
				
		for val in data['list']:
			
			temp_thumnail_id = 0
			
			id = val['id']
			name = val['name']
			businessEntity = val['businessEntity']
			industry = val['industry']
			description = val['description']
			website = val['website']
			city = val['city']
			country = val['country']
			rating = val['rating']
			reviewsCount = val['reviewsCount']
			jobsCount = val['jobsCount']
			latestReview = val['latestReview']
			logo = val['logo']
			
			new_company = WordPressPost()
			new_company.title = name
			new_company.content = description
			new_company.post_type = 'company'
			new_company.post_status = 'publish'
			
			new_company.id = wp.call(posts.NewPost(new_company))

			taxes = wp.call(taxonomies.GetTerms('company_category'))
			is_present = 0
			post_category_id = 0

			for val in taxes:
				if str(val) == str(industry):
					is_present = 1
					post_category_id = val.id
					break
				
			if is_present == 0:
				tag = WordPressTerm()
				tag.taxonomy = 'company_category'
				tag.name = industry
				post_category_id = wp.call(taxonomies.NewTerm(tag))

			category = wp.call(taxonomies.GetTerm('company_category', post_category_id))
			post = wp.call(posts.GetPost(new_company.id))

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
			print """ INSERT INTO clk_adefd4319e_wp_postmeta (post_id,meta_key,meta_value) VALUES ('"""+new_company.id+"""','_featured','0'); """
			cursor.execute(""" INSERT INTO clk_adefd4319e_wp_postmeta (post_id,meta_key,meta_value) VALUES ('"""+new_company.id+"""','_featured','0') """)
			db.commit()
			cursor.close()

			cursor = db.cursor()
			print """ INSERT INTO clk_adefd4319e_wp_postmeta (post_id,meta_key,meta_value) VALUES ('"""+new_company.id+"""','_company_tagline',''); """
			cursor.execute(""" INSERT INTO clk_adefd4319e_wp_postmeta (post_id,meta_key,meta_value) VALUES ('"""+new_company.id+"""','_company_tagline','') """)
			db.commit()
			cursor.close()
			
			cursor = db.cursor()
			print """ INSERT INTO clk_adefd4319e_wp_postmeta (post_id,meta_key,meta_value) VALUES ('"""+new_company.id+"""','_company_location','"""+str(country) + ', ' + str(city)+"""'); """
			cursor.execute(""" INSERT INTO clk_adefd4319e_wp_postmeta (post_id,meta_key,meta_value) VALUES ('"""+new_company.id+"""','_company_location','"""+str(country) + ', ' + str(city)+"""') """)
			db.commit()
			cursor.close()
			
			cursor = db.cursor()
			print """ INSERT INTO clk_adefd4319e_wp_postmeta (post_id,meta_key,meta_value) VALUES ('"""+new_company.id+"""','_company_website','"""+str(website)+"""'); """
			cursor.execute(""" INSERT INTO clk_adefd4319e_wp_postmeta (post_id,meta_key,meta_value) VALUES ('"""+new_company.id+"""','_company_website','"""+str(website)+"""') """)
			db.commit()
			cursor.close()
			
			cursor = db.cursor()
			print """ INSERT INTO clk_adefd4319e_wp_postmeta (post_id,meta_key,meta_value) VALUES ('"""+new_company.id+"""','_company_email',''); """
			cursor.execute(""" INSERT INTO clk_adefd4319e_wp_postmeta (post_id,meta_key,meta_value) VALUES ('"""+new_company.id+"""','_company_email','') """)
			db.commit()
			cursor.close()
			
			cursor = db.cursor()
			print """ INSERT INTO clk_adefd4319e_wp_postmeta (post_id,meta_key,meta_value) VALUES ('"""+new_company.id+"""','_company_phone',''); """
			cursor.execute(""" INSERT INTO clk_adefd4319e_wp_postmeta (post_id,meta_key,meta_value) VALUES ('"""+new_company.id+"""','_company_phone','') """)
			db.commit()
			cursor.close()

			cursor = db.cursor()
			print """ INSERT INTO clk_adefd4319e_wp_postmeta (post_id,meta_key,meta_value) VALUES ('"""+new_company.id+"""','_company_twitter',''); """
			cursor.execute(""" INSERT INTO clk_adefd4319e_wp_postmeta (post_id,meta_key,meta_value) VALUES ('"""+new_company.id+"""','_company_twitter','') """)
			db.commit()
			cursor.close()
			
			cursor = db.cursor()
			print """ INSERT INTO clk_adefd4319e_wp_postmeta (post_id,meta_key,meta_value) VALUES ('"""+new_company.id+"""','_company_facebook',''); """
			cursor.execute(""" INSERT INTO clk_adefd4319e_wp_postmeta (post_id,meta_key,meta_value) VALUES ('"""+new_company.id+"""','_company_facebook','') """)
			db.commit()
			cursor.close()
			
			cursor = db.cursor()
			print """ INSERT INTO clk_adefd4319e_wp_postmeta (post_id,meta_key,meta_value) VALUES ('"""+new_company.id+"""','_company_googleplus',''); """
			cursor.execute(""" INSERT INTO clk_adefd4319e_wp_postmeta (post_id,meta_key,meta_value) VALUES ('"""+new_company.id+"""','_company_googleplus','') """)
			db.commit()
			cursor.close()
			
			cursor = db.cursor()
			print """ INSERT INTO clk_adefd4319e_wp_postmeta (post_id,meta_key,meta_value) VALUES ('"""+new_company.id+"""','_company_linkedin',''); """
			cursor.execute(""" INSERT INTO clk_adefd4319e_wp_postmeta (post_id,meta_key,meta_value) VALUES ('"""+new_company.id+"""','_company_linkedin','') """)
			db.commit()
			cursor.close()
			

			cursor = db.cursor()
			print """ INSERT INTO clk_adefd4319e_wp_postmeta (post_id,meta_key,meta_value) VALUES ('"""+new_company.id+"""','_company_video',''); """
			cursor.execute(""" INSERT INTO clk_adefd4319e_wp_postmeta (post_id,meta_key,meta_value) VALUES ('"""+new_company.id+"""','_company_video','') """)
			db.commit()
			cursor.close()
			

			cursor = db.cursor()
			print """ INSERT INTO clk_adefd4319e_wp_postmeta (post_id,meta_key,meta_value) VALUES ('"""+new_company.id+"""','_thumbnail_id','"""+str(attachment_id)+"""'); """
			cursor.execute(""" INSERT INTO clk_adefd4319e_wp_postmeta (post_id,meta_key,meta_value) VALUES ('"""+new_company.id+"""','_thumbnail_id','"""+str(attachment_id)+"""') """)
			db.commit()
			cursor.close()

			cursor = db.cursor()
			print """ INSERT INTO clk_adefd4319e_wp_postmeta (post_id,meta_key,meta_value) VALUES ('"""+new_company.id+"""','mustakbil_company_id','"""+str(id)+"""'); """
			cursor.execute(""" INSERT INTO clk_adefd4319e_wp_postmeta (post_id,meta_key,meta_value) VALUES ('"""+new_company.id+"""','mustakbil_company_id','"""+str(id)+"""'); """)
			db.commit()
			cursor.close()
			

		count += 1

		if count > 2:
			break
		
	else:
		break