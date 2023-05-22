//  Put all include directives here

rule my_rule {
    /*
    Matching Modifiers:

    !     | negation    | Negates the match. This can be placed before other modifiers.
    sub:  | sub-search  | Match if this string appears anywhere.
    re:   | regex       | Match if the regular expression is satisfied.

    for more information, visit: https://github.com/ace-ecosystem/yara_scanner/tree/master
    */
    meta:
        // Matches everything past the first period in the file name.
        file_ext  = ""
        // Matches the full name of the file (not including the path.)
        file_name = ""
        // Matches against the full path of the file, if one was specified.
        full_path = ""
        // Matches against the output of file -b --mime-type.
        mime_type = ""

        // Severity information (will be used for fallback values as well)
        severity = "LOW"
        language = "..."

        // reference finding template
        ft_internal_id = "finding-template-title"
        ft_id = "FT-$uuid-$uuid"

        // Create a new finding template if none exists
        ft_fallback_title = "Place your title here"
        ft_fallback_description = "Description of the code/file finding"
        ft_fallback_risk = "Description of possible risks"
        ft_fallback_mitigation = "Possible mitigation description"

    strings:
        $name = "..."
    condition:
        any of them
}
