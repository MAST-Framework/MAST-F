rule AndroidLogging {
    meta:
        file_ext  = "smali"

        language = "smali"
        severity = "INFO"

        ft_internal_id = "android-logging"
        ft_fallback_title = "Android Logging"
        ft_fallback_description = "Logging is a common practice in Android app development for debugging purposes. However, logging can also introduce security risks if sensitive information is logged and the logs are not properly secured."
        ft_fallback_risks = "Sensitive information leakage: If sensitive information such as passwords, API keys, and user data is logged, it can be easily accessed by attackers who gain access to the logs. This can lead to data breaches and other security incidents; Code injection attacks: If logging statements are not properly sanitized, attackers can inject malicious code into the logs, which can then be executed when the logs are viewed or processed."
        ft_fallback_mitigation = "To mitigate this security risk, sensitive information such as passwords should never be logged. Instead, apps should use secure logging practices such as redaction or obfuscation of sensitive information, and ensure that logs are properly secured. Additionally, logs should be regularly reviewed and audited for any security incidents."
        ft_fallback_article = "android/logging"
    strings:
        $logMethods = /Landroid\/util\/Log;->(wtf|[deivw])\(/

    condition:
        any of them
}
