# School-Project-Weather **Global Warming**
## Slide 1: **Weathering Change: A Jersey City Climate Study**
### Science Meets Home: Investigating Jersey City's Changing Climate
<small>BY NIKITA EVTEEV</small>


## Slide 2: **Table of Contents**

Slides:  
1. Title
2. Table of Contents
3. Introduction  
4. Question  
5. Background Research  
6. Hypothesis  
7. Variables  
8. Materials 
9. Procedures  
10. Data  
11. Analysis  
12. Conclusion  
13. Thank You  


## Slide 3 **Introduction**

I will do a research on Global Warming topic looking at how temperature change in my home town.
In this project I will be learning basics on how to conduct scientific project, how to write a a code to get and to analyze historical tempreature. 
To do this I will use Python, Weather API (Application Programming Interface), GitHub with Codespaces, and Chat GPT for help. I will write the code in GitHub Codespaces using the Python extension and then running it to get all the information I need to complete this project. Since I can't get and analyze the weather data for the whole world, I will be using the weather data for New Jersey to complete my project in time.


## Slide 3 (cont): **Introduction/Background**

1. **Software Development**:  
   Software development are steps of creating code (software) that run on computers (hardware) to achieve certain goals. These steps are usually done by a team with help of development tools.

2. **Teamwork**:  
   Teamwork means working together to achieve a project goal. In our project, we’re working as a team, with me (Nikita), my dad and ChatGpt as a virtual assistant.

3. **GitHub**:  
   GitHub is an Internet tool to store and share programming code. It helps us work on the project together, and allows us to keep track of changes to the code.

4. **Development Environment (on GitHub Codespace)**:  
   A development environment is a place to write and test a code. On GitHub Codespaces, we can work in the cloud from Internet browser on any computer. It makes software development easier.

5. **Python**:  
   Python is a programming language we use to write the code. It's easy to learn and is perfect for working with data in scientific projects like ours.

6. **API (Application Programming Interface)**:  
   API is a way to get data from data source to process it in a code. Like in this project, the Python code is getting weather history from Open-Meteo.com using JSON API over HTTPS.

7. **HTTPS (HyperText Transfer Protocol Secure)**:  
   A secure version of HTTP, used to safely transfer data over the internet.

8. **JSON (JavaScript Object Notation)**:
   A format for storing and exchanging data, often used for APIs to send and receive information.


## Slide 4 **Questions**

1. **Is there global warming in New Jersey?**  
2. **Can I write a program to predict future temperature?**  
3. **How to conduct real-life scientific project**?  


## Slide 5: **Background Research**

Global warming causes glaciers to melt, which causes the sea levels to rise, which could cause some of the states to get flooded. This is especially bad for New Jersey because it is right next to the ocean.
Global warming is making it harder for plants to grow in many places because of less water, which could cause problems like hunger for many people.  
Global warming can be very dangerous because of this reason.


## Slide 6: **Hypothesis**

I have heard that Global Warming is severe issue. Though I can't tell if the temperature in New Jersey have gone up or down during last years, I can write a program to see the local weather change and even predict what the weather might be like in the future! 

## Slide 7: **Variables**

* Independent Variable:  
  - Date range for temperature increase (from January 1, 1964, to December 31, 2023).  
  - Date range for temperature prediction (from January 1, 2023, to December 4, 2024).  
  - Date (changing over time from January 1, 1964, to December 31, 2023).  
  - Year (to analyze average temperature change trends).  
* Dependent Variable:  
  - Daily temperature (collected frim data source).  
  - Average temperature (calculated per year).  
* Controlled Variables:  
  - Location: Jersey City, New Jersey.  
  - Data Type: Historical weather data (daily average temperatures).  
* Constant Variables:  
  - Measurement Units: Fahrenheit.  
  - Data Source: Open-Meteo.com.  
  - Calculation Method: Using the same formula for temperature trends and predictions.


## Slide 8: **Materials/Tools**

* GitHub with Codespaces.  
* Python.  
* Open-Meteo.com for past temperature in Jersey City.  
* Google Keep. 
* Chat GPT.


## Slide 9: **Procedures**

* Lear basics about project tools and concepts.  
* Setup project tools and development environment:  
  - Create Google Account for Google Keep and to register on GitHub. 
  - Create a GitHub repository.  
  - Configure GitHub Workspace for Python.  
  - Learn how to use Open-Meteo.com API.  
  
* Write the Python code on GitHub workspace.
* Get temperature data, display it for review and change the code if required.
* Use Chat GPT for help to write and fix the code.


## Slide 10: **Data**

* ![Yearly Average Plot](https://raw.githubusercontent.com/NKEvt/School-Project-Weather/99241539ddc2ac8299e472705892b38232dd5877/static/yearly-avg-plot.png)


<pre>
@equityit ➜ /workspaces/School-Project-Weather (development) $ /usr/local/bin/python /workspaces/School-Project-Weather/forecast-random-forest.py
Loaded data/20230101-20241204/openmeteo-20230101-20241204.csv with columns: ['time', 'temperature']
Model Mean Squared Error: 0.012590059657237803
Preparing next 10 days of predictions...
Next 10 Days Predictions:
2024-12-05: 2.59°C
2024-12-06: 3.88°C
2024-12-07: 4.60°C
2024-12-08: 5.02°C
2024-12-09: 5.20°C
2024-12-10: 5.01°C
2024-12-11: 4.24°C
2024-12-12: 3.19°C
2024-12-13: 2.30°C
2024-12-14: 1.40°C
</pre>


## Slide 11: **Analysis**

I asked my program to calculate the temperature difference between the years 1963 and 2023.  
The results showed that the temperature in New Jersey increases by 0.33 Celsius degrees every 10 years over this 60-years period. This rise shows a significant change in the temperature in New Jersey which can be caused by different things.  
I asked my program to predict the temprature for the next days using random forest training model and results of this prediction are on previous slide, these  temperature is to the real temperature.


## Slide 12: **Conclusion**

Through this project, I learned a lot about the effects of global warming and how temperatures are changing over time in Jersey City. By using Python, Open-Meteo API, GitHub, and Chat GPT as tools, I was able to:
Collect and analyze historical weather data.
Identify that the temperature in Jersey City has increased by 0.33°C every 10 years.
Predict future temperatures using machine learning (Random Forest model).
This confirms that global warming is an actual issue and may have a significant impact on our community. It is important to continue studying this problem.

Next Steps:
* Further Research: Investigate other regions to compare trends.  
* Self Improvements: Learn how to use computers for other projects.  
* Public Awareness: Share the results to show how to use existing free software tools for school projects and raise awareness about climate change.  

## Slide 13: **Thank You**
