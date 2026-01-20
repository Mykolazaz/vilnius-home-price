# Apartment Prices in Vilnius

This is a Python data scraping and prediction project with Selenium & Pandas.

The main goal of this project is to build a tool that **predicts** apartment prices in Vilnius based on area, floor, location, proximity to key buildings and text descriptions in listings.

The data was scraped from [Aruodas.lt](https://aruodas.lt/), the most popular Lithuanian real estate marketplace.

The XGBoost model is deployed on [manobustokaina.lt](https://www.manobustokaina.lt/).

#### Achieved outcomes:

- The XGBoost model achieves an R<sup>2</sup> of 0.894 ± 0.015, with an average prediction error of approximately 21%. This provides a solid baseline for estimating apartment prices in Vilnius.
- Area is the most significant predictor of price. Year of construction and location also play crucial roles.
- The model struggles with non-standard properties (such as lofts in industrial zones, ultra-luxury apartments) and listings with incomplete data. The discrepancy arises from qualitative factors ('prestige', condition of the building's exterior & apartment interior) that are not fully captured by tabular data.

#### What can be improved?
1. Image analysis: Incorporating image analysis (listing photos) could help assess the condition (renovation quality, view) better than binary features like `renovated`.
2. Micro-location: Developing a `neighborhood score` could help differentiate between different areas that are equally far from the center but have vastly different market values.
3. Other models: Experimenting with other gradient boosting frameworks like LightGBM might help achieve higher accuracy.
4. Confidence interval: Predicting a price interval would be valuable for users, indicating when the model is uncertain.
5. SHAP values for users: Displaying SHAP values in the deployed application would provide transparency, helping users understand why a specific price was predicted.


![Application Image](./app-image.png)

AI was used for debugging, model variable preparation, multiple language & map implementation in deployment app and general improvement suggestions (without code).