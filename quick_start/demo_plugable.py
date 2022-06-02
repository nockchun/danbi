import danbi as di

# Create Plugin Manager
print("---------------------------- Create Manager ----------------------------")
plugin_manager = di.PluginManager("plugins")
print(plugin_manager.getPlugins(), "\n")

# Start Plugin
injection_map = {
    "flask:app": 123,
    "postgresql:connection": 456
}

print("----------------------------- Start Plugin -----------------------------")
plugin_manager.plug(injection_map)
print()

print("----------------------------- Stop Plugin ------------------------------")
plugin_manager.unplug("plugins.TinyService.TinyService")
plugin_manager.plug(injection_map, "plugins.TinyService.TinyService")
plugin_manager.plug(injection_map, "plugins.sub_plugin.SubService.SubService")
plugin_manager.unplug()
