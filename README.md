# Apartment Prices in Vilnius

This is a Python data scraping and prediction project with Selenium & Pandas.

The main goal of this project is to **predict** apartment prices in Vilnius based on area, floor, location, proximity to amenities and text descriptions in listings.

The data was scraped from [Aruodas.lt](https://aruodas.lt/), the most popular Lithuanian real estate marketplace.

Achieved outcomes:

- an XGBoost model that achieves an R<sup>2</sup> of 0.883 ± 0.015 and RMSLE is 0.19.

- best apartment price predicting variables were area, build year and location based variables such as longitude, latitude and whether the apartment is located in Senamiestis;

- the current model could be further improved by extracting missing categorical features from text and exploring other location-based features.

The XGBoost model is deployed on [Heroku](https://vilnius-nostradamus-095f0ef45495.herokuapp.com/).

![alt text](./vilnius-nostradamus.png)

AI was used for debugging, model variable preparation & map implementation in deployment app and general improvement suggestions (without code).