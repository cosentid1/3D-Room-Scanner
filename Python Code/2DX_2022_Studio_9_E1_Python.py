import serial, numpy, open3d, math  #Importing necessary packages

connection = serial.Serial('COM3',115200) # Setting the connection
connection.open  # Opening the connection
connection.reset_output_buffer() # Resetting the output buffer of the connection
connection.reset_input_buffer() # Resetting the input buffer of the connection


step_val = 0 # Variable to keep track of the number of steps
x_axis_displacement = 0 # Keeps track of the total displacement along the x-axis (mm)
total_spins_val = 32  # 360deg/32 total spins = 11.25deg/spin   
count_num = 0 # Counter to keep track for the while loop
all_vertices_val = []  # List created to store the vertices with a value
total_line_set = []  # Creating coordinates to connect all the lines for the vertices
vals_file = open("2DX3_DEL2_VALS.xyz", "w") # Opening the file in write mode is prior main_content is overwritten

num_scans_val = input("How many times will you be scanning?\nIf you will not, please type 0 to end the program. ") # Stores the number of scans
while (not(num_scans_val.isdigit())):
    num_scans_val = input("\nPlease try again.\nHow many times will you be scanning?\nIf you will not, please type 0 to end the program. ")  # Trys again if while loop condition not met
if (int(num_scans_val) == 0):
    print("Exiting the program")    # Exits the program is 0 is inputted, otherwise stores a valid numerical number of scans
    raise SystemExit
num_scans_val = int(num_scans_val) # Assigns the integer version of itself to itself

if (num_scans_val > 1): # Asks for the increase in value in the x-axis after the first scan, only if the total number of scans is greater than 1
    x_increase = input("\nEnter the magnitude of displacement there will be along the x-axis (mm).\nIf there won't be any, please type 'none'. ")   # Value for setting the distance for moving along the x-axis (mm)
    while (not(str(x_increase).isdigit())):  # Uses the isdigit() method to check if the string version of the variable is NOT digits
        if (x_increase.isdigit()):  # Also takes care of the condition where the user purposely types "0"
            x_increase = int(x_increase)  # Assigns the integer version of itself to itself
        elif (x_increase.lower() == "none"):             # Conditions for valid x-axis increase values
            x_increase = 0  # Sets the x_axis displacement value increaser to 0
        else:
            x_increase = input("\nInvalid input.\nEnter the magnitude of displacement there will be along the x-axis (mm).\nIf there won't be any, please type 'none'. ")   # Otherwise repeats

print("\nPlease press the button to start getting measurements now\n")  # Tells the user to press the start button on the MCU
while(count_num < num_scans_val): # Runs until the number of scans is satisfied as defined by the user
    main_content = (connection.readline()).decode("utf-8") # Uses the decode method to decode a byte of the data transmitted with UART into a string
    main_content = main_content[0:-2] # Optimizing the main data format from the string so it can be utilized)
    if (main_content.isdigit() == True): # Only looks at content if it is a digit
        if (step_val == 0 and num_scans_val < 2):
            print("Starting at x_comp = 0") # Prints this message if there is only one scan being done
        if (int(main_content) == 0):
            print("No measurement")  # If the data_true variable is LO in the hardware code and the UART transmit 0, then print this message and doesn't add anything to the file
        else :
            angle_val = (step_val / 512) * math.pi * 2 # Gets the angle value by performing the calculation  
            y_component = int(main_content) * math.cos(angle_val) # Calculates the y component from the distance
            z_component = int(main_content) * math.sin(angle_val) # Calculates the z component from the distance
            print(f"x_comp: {x_axis_displacement}, y_comp: {y_component:.3f}, z_comp: {z_component:.3f}")  # Prints the 3 plane component values 
            vals_file.write('{} {} {}\n'.format(x_axis_displacement,y_component,z_component)) # Writes the appropriate x,y,z files into the .xyz file
        step_val = step_val + 16  # Increments by 16 as we want 32 movements of the motor (32*16 = 512)
    if (step_val == 512): # If motor has doen full rotation, resets the variable so further rotations can be done if needed
        step_val = 0  # Resets by setting to 0
        count_num+= 1 # Increments the scan counter
        if (num_scans_val > 1): # Only adds the displacement to the x-axis if the nnumber of scans is greater than 1
             x_axis_displacement = x_axis_displacement + int(x_increase)  # Adds the displacement along the a-axis 
        if (count_num < num_scans_val):  # Prints instructions if there will be more scans
            print("\nWaiting for next button press\n")
vals_file.close() #close file when done so the content gets saved

for vertice_value in range(0, total_spins_val * num_scans_val):
    all_vertices_val.append([vertice_value])  # Appending to the list
for actual_value in range(0, total_spins_val * num_scans_val, total_spins_val):
    for val in range(total_spins_val):    # Nested for loop to iterate through all of them
        if val == total_spins_val - 1:
            total_line_set.append([all_vertices_val[actual_value + val], all_vertices_val[actual_value]])  # Appending to the list depending on the condition
        else:
            total_line_set.append([all_vertices_val[actual_value + val], all_vertices_val[actual_value + 1 + val]])     
for actual_value in range(0, (total_spins_val * num_scans_val) - total_spins_val - 1, total_spins_val):  # Producing the coordinates to connect them all   
    for val in range(total_spins_val):
        total_line_set.append([all_vertices_val[actual_value + val], all_vertices_val[actual_value + total_spins_val + val]])  # Appending to the list
        
visualization = open3d.io.read_point_cloud("2DX3_DEL2_VALS.xyz", format="xyz") # Saving to a variable    
point_visualization = open3d.geometry.LineSet(points=open3d.utility.Vector3dVector(numpy.asarray(visualization.points)),lines=open3d.utility.Vector2iVector(total_line_set))  # Equating it to a variable
print("\nThe cloud form of the data points has been displayed")  # Instructions for the user
open3d.visualization.draw_geometries([visualization])  # Opens the cloud form of the data points with open3d
print("\nThe graphical form of the data points with connecting lines has been displayed")  # Instructions for the user
open3d.visualization.draw_geometries([point_visualization])  # Opening the graphical view of the final spatial mapping image with the vertices connected with lines
print("\nThank you for using this program!") # Final message to the user :)
