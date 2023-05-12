rule NativeLibraryLoaded
{
    meta:
        template_id = "FT-..."
    strings:
        $method_call = "Ljava/lang/Exception;->printStackTrace"
    condition:
        any of them
}
