from mastf.MASTF.utils.helpers import new_error

########################################################################
# Errors
########################################################################
UNKNOWN_PROJECT_ID = 0x4000
INVALID_PROJECT_FORM = 0x4001
INVALID_SCAN_FORM = 0x4002

ERRORS = {
    
    UNKNOWN_PROJECT_ID: new_error(title="Unknown Project-ID", description="Project-ID invalid or not found"),
    INVALID_PROJECT_FORM: new_error(title="Invalid Project-Form"),
    INVALID_SCAN_FORM: new_error(code=507, title="Invalid Form", 
        description="Could not verify Scan-Form - there might be an issue with the transmitted data!")
    
    
}

########################################################################
# Templates
########################################################################
TMP_OVERVIEW = "project/project-overview.html"
TMP_ERROR = "error.html"
