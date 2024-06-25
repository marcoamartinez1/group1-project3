# group1-project3
Group 1's work product for Project 3.

For project 3, our group created a dashboard that compares data from cellular network providers in a bar chart and map.

We collected the data from the Federal Communications Commission's "Measuring Broadband America" initiative.
We used the full-year 2022 data that can be found here: https://www.fcc.gov/reports-research/reports/measuring-broadband-america/measuring-broadband-america-mobile-data

This data was cleaned and analyzed in Jupyter Notebook and exported as a csv into pymongo. From pymongo we loaded it into a Flask App in python.

We used the glob python library when cleaning the data. This was not shown in class and fulfills the requirement of using a new library.

Generating the choropleth map required the merging of a geoJSON file of state information with averages we found in our analysis. The merge was found with help of online tools and the file to merge was found on Kate Gallo's profile on Kaggle (https://www.kaggle.com/datasets/pompelmo/usa-states-geojson)

We created JavaScript and HTML files to create and show the visualizations.

The localhost page launches from the app.py file in the flask folder. You can open the integrated terminal and call "python app.py"

We received help from online documentation for certain libraries, AI tools like ChatGPT and the Xpert Learning Assistant, and forums like Stack Overflow.

Ethical considerations:
The data we used was collected by volunteers on behalf of the Federal Communications Commission. Our manipulations of the data were not bad faith efforts to misrepresent or coerce the data into any findings that were biased. We cleaned data to make it easier to deal with on our end and that would not overwhelm any systems we created around it. We did our best to avoid biases and maintain integrity of the findings. In the case of the choropleth map, there were no tests completed for the state of Alaska for T-Mobile. As such, Alaska was removed from the map. We don't believe this affects our data, though, of course, it would be better to have information for all states and all carriers. We added the "Tests per State per Carrier" list as a way to be up front about the map and allow a user to further investigate the data being shown.
