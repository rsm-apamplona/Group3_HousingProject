from shiny import App, ui

#Screenshot URL
src = "https://raw.githubusercontent.com/rsm-apamplona/Group3_HousingProject/refs/heads/main/Shiny%20Code/Screenshot%202024-11-01%20145938.png?token=GHSAT0AAAAAACYJ6MBJGSSPQTKTXDRB62GAZZHQ67Q"

# Define the UI
app_ui = ui.page_fluid(
    ui.h2("Group 3 Shiny Document Overview"),
    
    # Add your UI components here
    ui.h3("Process"),
    ui.p("""We started our project like most people by Googling and seeing what 
		public datasets were available. We noticed Zillow had an API and 
		lots of public data sets available and even in 2017 hosted a contest 
		to try to improve their algorithm with a 1 million dollar cash prize."""),
    ui.h3("Hurdles"),
    ui.p("""Upon investigating and digging deeper we saw that Zillow didn’t share 
	their data on price per square foot for homes. The team thinks that’s 
	due to Zillow’s proprietary algorithm in how they rank homes. 
    """),
    ui.h3("Limitations"),
    ui.p("""The group attempted to scrape live Refin listings to gather price, 
	address, and square footage using Beautifulsoup but was blocked by 
	Refin."""),
    ui.card(
        ui.card_header("RedFin Rejection Screenshot"),
        ui.img(
            src=src,
            alt="RedFin Rejection Screenshot",
            width="600px"
        )
    )
    # ui.button("This is a button."),
    # ui.text_input("This is a text input."),
    # ui.checkbox("This is a checkbox."),
)

# Define the server function (empty here, as no reactive logic is needed)
def server(input, output, session):
    pass

# Create the Shiny app
app = App(app_ui, server)
