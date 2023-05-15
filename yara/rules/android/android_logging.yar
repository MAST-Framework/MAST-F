rule AndroidLogging {
    meta:
        file_ext  = "smali"

        language = "smali"
        severity = "INFO"

        ft_internal_id = "android-logging"

        ft_fallback_title = "Android Logging"
        ft_fallback_description = "The App may be logging sensitive information. Make"
    strings:
        $logMethods = /invoke-.*?/{(Landroid/util/Log;->(v|d|i|w|e|wtf)([^}]+})/ nocase

    condition:
        $logMethods
}
