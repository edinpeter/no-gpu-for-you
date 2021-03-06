from flask import Flask

app = Flask(__name__)

# Flask endpoints

@app.route('/status/')
def home():
	log = open('iter.txt', 'r')
	iteration = log.readlines()
	log.close()
	return str(iteration)

app.run(host="0.0.0.0", port="5000")

if __name__ == "__main__":
	pass
