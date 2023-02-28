# Diary
**Your Trusted Companion**<br/>
Through our innovative diary writing web application, we hope to empower individuals to cultivate a lifelong habit of self-reflection and personal growth. We strive to provide a secure and private environment for users to express their deepest thoughts and emotions, reflect on their experiences, and gain insights into their lives. Our mission is to inspire and support people on their journey of self-discovery, fostering greater self-awareness and assisting them in living more fulfilling and meaningful lives.

## Pre-requisites<br/>
You should have installed Python and PostgreSQL inorder to run the project.<br/>
## Project Setup<br/>
### Run the following commands:<br/>
*git clone https://github.com/Abekaesh/Diary.git<br/>
cd Diary<br/>
python3 -m venv venv<br/>
source venv/bin/activate<br/>
pip install flask<br/>
pip install flask_session<br/>
pip install psycopg2-binary<br/>
pip install functools<br/>*
### Open new terminal and type the commands for setting up of database:<br/>
*sudo -i -U postgres<br/>
psql<br/>
CREATE DATABASE diary;<br/>
\c diary<br/>
CREATE TABLE users (
  user_id INT PRIMARY KEY,
  name VARCHAR(255),
  email VARCHAR(255),
  password VARCHAR(255)
);<br/>
CREATE TABLE diary_entry (
  entry_id INT PRIMARY KEY,
  user_id INT,
  entry_text TEXT,
  created_at DATE DEFAULT CURRENT_DATE,
  FOREIGN KEY (user_id) REFERENCES users(user_id)
);<br/>
CREATE TABLE tags (
  tag_id INT PRIMARY KEY,
  tag_name VARCHAR(255)
);<br/>
CREATE TABLE entry_tag (
  entry_id INT,
  tag_id INT,
  PRIMARY KEY (entry_id, tag_id),
  FOREIGN KEY (entry_id) REFERENCES diary_entry(entry_id),
  FOREIGN KEY (tag_id) REFERENCES tags(tag_id)
);<br/>*
### Project execution command:<br/>
*python3 -m flask run*





