from system_message import adhoc_files_mapping

# Tool definitions for the Model
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_dqr_summary",
            "description": "Function to answer user queries about DQR. This function returns a data chunk which can be used to answer the user queries.\
                This function should be used to answer any queries which require any data access to the summary files.",
            "parameters": {
                "type": "object",
                "properties": {
                    "state": {
                        "type": "string",
                        "description": "US state code only (eg. FL for Florida and AZ for Arizona). If not specified, use FL. Using full state name is not allowed."
                    },
                    "refresh_month": {
                        "type": "string",
                        "description": "Refresh month for which the feed files are to be used in the format PT_MMM_YYYY. If not specified, use the most recent refresh month and year available. should not be confused with member month."
                    },
                    "lob": {
                        "type": "string",
                        "enum": ["Medicaid", "Medicare"],
                        "description": "Line of Business (LOB). If not specified, use Medicaid."
                    },
                    "feed": {
                        "type": "string",
                        "description": "Type of feed file. To be selected out of the file types provided."
                    },
                    "stat_file": {
                        "type": "string",
                        "enum": ["EDD", "FreqDist", "DAT"],
                        "description": "Type of summary file build upon the feed file"
                    },
                    "column": {
                        "type": "string",
                        "description": "The column in the feed file to summarize"
                    }
                },
                "required": ["state", "refresh_month", "lob", "feed", "stat_file", "column"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "plot_chart",
            "description": "Create a chart/trendline using the given X and Y data and labels, with a specified chart type. This helps create any type of graphical representation\
                of the data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "x_label": {
                        "type": "string",
                        "description": "Label for the x-axis"
                    },
                    "x_data": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Values for the x-axis"
                    },
                    "y_label": {
                        "type": "string",
                        "description": "Label for the y-axis"
                    },
                    "y_data": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Values for the y-axis"
                    },
                    "chart_type": {
                        "type": "string",
                        "enum": ["line", "bar", "scatter", "histogram"],
                        "description": "Type of chart to generate"
                    },
                    "title": {
                        "type": "string",
                        "description": "Title of the chart"
                    }
                },
                "required": ["x_label", "x_data", "y_label", "y_data"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "adhoc_checks",
            "description": "Function to answer user queries about adhoc checks. This function returns a data chunk which can be used to answer the user queries.",
            "parameters": {
                "type": "object",
                "properties": {
                    "state": {
                        "type": "string",
                        "description": "Name of the US state in state code format(eg. FL for Florida and AZ for Arizona). If not specified, use FL."
                    },
                    "refresh_month": {
                        "type": "string",
                        "description": "Refresh month for which the feed files are to be used in the format PT_MMM_YYYY. If not specified, use the most recent refresh month and year available. should not be confused with member month."
                    },
                    "lob": {
                        "type": "string",
                        "enum": ["Medicaid", "Medicare"],
                        "description": "Line of Business (LOB). If not specified, use Medicaid."
                    },
                    "checks": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "enum": adhoc_files_mapping,
                        "description": "Array of adhoc checks. To be selected out of the file types provided. This of be of the format ['check1', 'check2']"
                    }
                },
                "required": ["state", "refresh_month", "lob", "checks"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "plot_chart",
            "description": "Create a chart/trendline using the given X and Y data and labels, with a specified chart type. This helps create any type of graphical representation\
                of the data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "x_label": {
                        "type": "string",
                        "description": "Label for the x-axis"
                    },
                    "x_data": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Values for the x-axis"
                    },
                    "y_label": {
                        "type": "string",
                        "description": "Label for the y-axis"
                    },
                    "y_data": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Values for the y-axis"
                    },
                    "chart_type": {
                        "type": "string",
                        "enum": ["line", "bar", "scatter", "histogram"],
                        "description": "Type of chart to generate"
                    },
                    "title": {
                        "type": "string",
                        "description": "Title of the chart"
                    }
                },
                "required": ["x_label", "x_data", "y_label", "y_data"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cmp_dqr",
            "description": "Function to compare DQR summary files. this function returns a data chunk which can be used to answer the user queries related to DQR comaparisons month over month.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lob": {
                        "type": "string",
                        "enum": ["Medicaid", "Medicare"],
                        "description": "Line of Business (LOB). If not specified, use Medicaid."
                    },
                    "state": {
                        "type": "string",
                        "description": "Name of the US state in state code format(eg. FL for Florida and AZ for Arizona). If not specified, use FL."
                    },
                    "refresh1": {
                        "type": "string",
                        "description": "Refresh month for which the feed files are to be compared with the previous month in the format PT_MMM_YYYY. If not specified, use the most recent refresh month and year available. should not be confused with member month."
                    },
                     "refresh2": {
                        "type": "string",
                        "description": "Previous refresh month for which the feed files are to be used to be compared with a newer refresh month in the format PT_MMM_YYYY. If not specified, use the second most recent refresh month and year available. should not be confused with member month."
                    },
                },
                "required": ["lob", "state", "refresh1", "refresh2"]
            }
        }
    }
]


