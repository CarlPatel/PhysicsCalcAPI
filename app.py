from flask import Flask, request, jsonify, make_response, json
from flask_cors import CORS, cross_origin
import math





app = Flask(__name__) 
#app.secret_key = "asdf"

@app.route("/", methods=["GET"])

@cross_origin(supports_credentials=True)



def unit():
	"""
	link: www.api.com/api?force=1&mass=2
	http://localhost:5000/api?unit=kinematics&final%20velocity=3&displacement=3&initial%20velocity=-4
	http://localhost:5000/api?unit=forces&acceleration=2&force=3
	http://localhost:5000/api?unit=gravitation&mass1=2&radius=3&mass2=5

	https://physicscatalyst.com/calculators/physics/kinematics-calculator.php
	"""
	global file, unit
	unit = request.args.get("unit")

	with open('Equations.json') as f:
		file = json.load(f)
	file = file[unit]

	if unit == "kinematics":
		return kinematics()
	else:
		return only1Ans()



def only1Ans():

	variables = file["variables"]["type"]
	numOfVariables = 0
	variableDict = {}

	for i,j in variables.items():

		globals()[j] = request.args.get(i)
		if (globals()[j]=="null"):
			globals()[j]=None

		variableDict[i] = ((globals()[j]))

		if globals()[j] != None and (globals()[j].isnumeric() or (globals()[j][1:].isnumeric() and globals()[j][0] == "-")):
			globals()[j] = (float(globals()[j]))
			variableDict[i] = (float(globals()[j]))
			numOfVariables += 1
		else:
			if globals()[j] != None:
				return response(400, "You must enter a number")


	necessaryNumOfVariables = file["variables"]["necessary"]


	if numOfVariables == necessaryNumOfVariables:
		for i in variableDict:
			if variableDict[i]==None:
				subject=[i]
				break


		try:
			ans = (eval(getEquation(subject)[0]))
		except ZeroDivisionError:
			return response(400,"You can't divide by zero")
		except ValueError:
			return response(400,"You can't sqrt a negative number")
		except:
			return response(400,"Error")


		return response(200, format(subject[0], prettyAns(ans, subject[0]), getEquationPretty(subject),EquationWithNumbers(subject)))

	elif numOfVariables < necessaryNumOfVariables:
		return response(400, "You need to fill in " + str(necessaryNumOfVariables) + " variables")
	elif numOfVariables > necessaryNumOfVariables:
		return response(400, "You can only have " + str(necessaryNumOfVariables) + " variables filled in")
	return response(200, variableDict)



def kinematics():
	
	variables = file["variables"]["type"]
	numOfVariables = 0
	variableDict = {}

	for i,j in variables.items():

		globals()[j] = request.args.get(i)
		if (globals()[j]=="null"):
			globals()[j]=None

		variableDict[i] = ((globals()[j]))

		if globals()[j] != None and (globals()[j].replace(".","").isnumeric() or (globals()[j][1:].replace(".","").isnumeric() and globals()[j][0] == "-")):
			globals()[j] = (float(globals()[j]))
			variableDict[i] = (float(globals()[j]))
			numOfVariables += 1
		else:
			if globals()[j] != None:
				return response(400, "You must enter a number")

	
	necessaryNumOfVariables = file["variables"]["necessary"]


	if numOfVariables == necessaryNumOfVariables:
		for i in variableDict:
			if variableDict[i]==None:
				subject=[i]
				break
		for i in variableDict:
			if i != subject[0] and variableDict[i]==None:
				without=[i]
				break
		subject.append(without[0])
		without.append(subject[0])

		try:
			ans1 = eval(getEquation(subject,without)[0])
		except ZeroDivisionError:
			return response(400,"You can't divide by zero")
		except ValueError:
			return response(400,"You can't sqrt a negative number")
		except:
			return response(400,"Error")

		try: 
			ans2 = eval(getEquation(subject,without)[1])
		except ZeroDivisionError:
			return response(400,"You can't divide by zero")
		except ValueError:
			return response(400,"You can't sqrt a negative number")
		except:
			return response(400,"Error")


		#return response(200, variableDict)

		return response(200, format(subject[0], prettyAns(ans1, subject[0]), getEquationPretty(subject,without),EquationWithNumbers(subject,without), subject[1], prettyAns(ans2, subject[1])))

	elif numOfVariables < necessaryNumOfVariables:
		return response(400, "You need to fill in " + str(necessaryNumOfVariables) + " variables")
	elif numOfVariables > necessaryNumOfVariables:
		return response(400, "You can only have " + str(necessaryNumOfVariables) + " variables filled in")
		


def prettyAns(ans, subject):
	with open('Units.json') as u:
		units = json.load(u)

	ans = roundNum(ans)

	try:
		return str(ans) + " " + units[subject]
	except:
		return ans

def roundNum(num):
	if num == None:
		num = None
	elif (num < 0.0001 and num > -0.0001 and not num == 0) or num > 9999 or num < -9999:
		num = "{:.4e}".format(num)
	elif num%1 != 0:
		num = round(num, 4)
	else:
		num = int(num)

	return num

def getEquation(subject, without=None):
	equations = file["equations"]
	if unit == "kinematics":
		return [equations[subject[0]][without[0]],equations[subject[1]][without[1]]]
	else:
		return [equations[subject[0]]]


def getEquationPretty(subject, without=None):
	equations = file["equations"]
	if unit == "kinematics":
		Equations = [equations[subject[0]][without[0]],equations[subject[1]][without[1]]]
	else:
		Equations = [equations[subject[0]]]

	for i in range(len(Equations)):
		if "math.sqrt" in Equations[i]:
			Equations[i] = Equations[i].replace("math.sqrt", "sqrt")

	return Equations


def EquationWithNumbers(subject, without=None):
	variables = file["variables"]["type"]
	if unit == "kinematics":
		Equations = getEquation(subject,without)
	else:
		Equations = getEquation(subject)


	for k in range(len(Equations)):
		if "sqrt" in Equations[k]:
			equation = Equations[k].split("math.sqrt")
			for i in range(len(equation)):
				for j in variables.values():
					equation[i] = equation[i].replace(j,str(roundNum(eval(j))))
			Equations[k] = "sqrt".join(equation)

		else:
			for i in range(len(Equations)): 
				for j in variables.values():
					Equations[i] = Equations[i].replace(j,str(roundNum(eval(j))))

	return Equations


def format(solvedFor1, ans1, equation, equationwithnumbers, solvedFor2=None, ans2=None):
	if unit == "kinematics":
		return jsonify({
			"Status":"success",
			"SolvedFor1": str(solvedFor1),
			"SolvedFor2": str(solvedFor2),
			"Answer1":str(ans1),
			"Answer2":str(ans2),
			"Equation1":str(equation[0]),
			"Equation2":str(equation[1]),
			"EquationWithNumbers1":str(equationwithnumbers[0]),
			"EquationWithNumbers2":str(equationwithnumbers[1]),
			})
	else:
		return jsonify({
			"Status":"success",
			"SolvedFor": str(solvedFor1),
			"Answer":str(ans1),
			"Equation":str(equation[0]),
			"EquationWithNumbers":str(equationwithnumbers[0]),
			})


def response(code, data):
	if code == 400:
		r = make_response(jsonify({"Status":"fail","Error": data}), code)
	else:
		r = make_response(data, code)

	r.headers["Content-Type"] = "application/json"
	return r



if __name__ == "__main__":
	app.debug = True
	app.run("localhost", 5000)
	