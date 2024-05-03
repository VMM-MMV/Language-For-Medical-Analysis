from temp import *
import json
import os
import textwrap
parser: Parser = Parser()
code: str = r"""
# Create Template {
#     name: Heart_2
#     params: {
#         ST_Slope: str
#         Oldpeak: float
#         ExerciseAngina: str
#         MaxHR: int
#         RestingECG: str
#         FastingBS: float
#         Cholesterol: float
#         RestingBP: int
#         ChestPainType: str
#         Sex: str
#         Age: int
#     }
#     target: {diagnosis: float}
#     data: "C:\Users\Jora\Medic"
# }

declare Person = Obesity {
    pregnancies: 1
    glucose: 110
    bloodPressure: 50
    skinThickness: 25
    insulin: 100
    # bmi: 1
    age: 30
}

Person.predict

# declare Person = Heart {
#     # ST_Slope can be Up, Flat, Down 
#     ST_Slope: 'Up'
#     Oldpeak: 3
#     # Exercise Angine can be N, Y
#     ExerciseAngina: 'Y'
#     MaxHR: 150
#     # Resting ECG can be Normal, ST, LVH
#     RestingECG: 'Normal'
#     FastingBS: 120
#     Cholesterol: 200
#     RestingBP: 120
#     # Chest Pain Type can be ATA, NAP, ASY, TA
#     ChestPainType: 'ATA'
#     # Sex can be M, F
#     Sex: 'M'
#     Age: 45
# }

# Person.predict

"""
result: dict = parser.parse(code)
    
class Compiler:
    def getIndent(self, indent):
        return " " * indent
    def ClassMethods(self, indent):
        code_block = """
def visualize(self):
    print("Here Add Vizualization Type Stuff or not")

def predict(self):
    print("Here Add Data Science Type Stuff")

def load(self):
    return pd.load(self.data_path)
    
"""

        indented_code_block = textwrap.indent(code_block, prefix=" " * indent)
        return self.getIndent(indent) + indented_code_block 

    def handleBinaryExpression(self, node):
        if not node:
            return
        
        if node.get("expression"):
            node = node["expression"]

        if node["type"] == "BinaryExpression":
            return f"({self.handleBinaryExpression(node['left'])} {self.handleBinaryExpression(node['operator'])} {self.handleBinaryExpression(node['right'])})"
        else:
            return str(node["value"])
    
    def handleVariableDeclaration(self, node, indent):
        node = node["declarations"]
        return self.getIndent(indent) + f"{node['id']['value']} = {self.handleBinaryExpression(node['init'])}"
    
    def handleClassCreation(self, node, indent):
        class_code = "\n" + self.getIndent(indent) + "class " + node["name"] + ":" + "\n"
        indent += 4
        class_parameters_code = self.getIndent(indent) + "def __init__(self"
        class_body_code = ""
        indent += 3

        for parameter in node["parameters"]:
            parameters = self.handleVariableDeclaration(parameter, indent)
            var_name, var_type = [x.strip() for x in parameters.split(" = ")]
            class_parameters_code += f", {var_name}: {var_type}"
            class_body_code += "\n" + self.getIndent(indent+1) + f"self.{var_name} = {var_type}({var_name})"
            
        target = self.handleVariableDeclaration(node["target"], indent)
        var_name, var_type = [x.strip() for x in target.split(" = ")]
        # TODO add vartype to check which type of regression to do
        # int thefore logistic, float linear
        class_parameters_code += f", {var_name} = None"
        class_body_code += "\n" + self.getIndent(indent+1) + f"self.target: {var_type} = '{var_name}'"

        class_body_code += "\n" + self.getIndent(indent+1) + f"self.data_path = str(r{node['data_path']})"
        
        class_parameters_code += "):"
        class_code += class_parameters_code + "\n"
        class_code += class_body_code + "\n"
        class_code += self.ClassMethods(indent=indent-3)
        templates_path = "Templates"

        if not os.path.exists(templates_path):
            os.mkdir(templates_path)
            os.mknod(templates_path+"/__init__.py")

        with open(f"{templates_path}/{node['name']}.py", "w+") as f:
            f.write(class_code)
        return class_code

    def handleClassInitialization(self, node, indent):
        class_init_code = f"from Templates.{node['class_type']} import * \n"
        class_init_code += f"{node['name']} = {node['class_type']}("

        indent += 3

        for parameter in node["declarations"]:
            parameters = self.handleVariableDeclaration(parameter, indent)
            var_name, var_type = [x.strip() for x in parameters.split(" = ")]
            class_init_code += f"{var_name} = {var_type}, "
        class_init_code = class_init_code[:-2]
        class_init_code += ")"
        return class_init_code
    
    def handleMethodCall(self, node, indent):
        return self.getIndent(indent) + f"{node['class_type']}.{node['method_name']}()"
        
    def handleBlock(self, node, indent):
        self.code = ""
        def walkAst(node, indent):
            if not node:
                return

            # try:
            #     # print(node['type'])
            # except:
            #     pass
            
            if node["type"] == "ExpressionStatement":
                self.code += "\n"
                self.code += self.getIndent(indent) + str(self.handleBinaryExpression(node))
                return

            if node["type"] == "InitStruct":
                self.code += "\n"
                self.code += self.getIndent(indent) + str(self.handleClassCreation(node, indent))
                return

            if node["type"] == "NewStruct":
                self.code += "\n"
                self.code += self.getIndent(indent) + str(self.handleClassInitialization(node, indent))
                return
            
            if node["type"] == "MethodCall":
                self.code += "\n"
                self.code += self.getIndent(indent) + str(self.handleMethodCall(node, indent))
                return
            
            if node["type"] == "VariableDeclaration":
                self.code += "\n"
                self.code += self.getIndent(indent) + str(self.handleVariableDeclaration(node, indent))
            
            if node["type"] == "PrintStatement":
                self.code += "\n"
                self.code += self.getIndent(indent) + f"print({self.handleBinaryExpression(node)})"
                
            for key, value in node.items():
                if key != 'type' and isinstance(value, dict):
                    walkAst(value, indent)  # Child node
                elif key != 'type' and isinstance(value, list):
                    for item in value:
                        walkAst(item, indent)  # Items within a list            
            
        walkAst(node, indent)
        return self.code

if __name__ == "__main__":
    compiler = Compiler()
    code = compiler.handleBlock(result, 0)
    print(code)
    exec(code)