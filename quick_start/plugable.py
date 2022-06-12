import danbi as di

# Create Plugin Manager
print("---------------------------- Create Manager ----------------------------")
plugin_manager = di.PluginManager().addPackagePath("plugins")
print(plugin_manager.getPlugins(), "\n")

print("----------------------------- Start Plugin -----------------------------")
plugin_manager.plug()
print()

print("----------------------------- Stop Plugin ------------------------------")
plugin_manager.unplug("plugins.TinyService.TinyService")
plugin_manager.plug("plugins.TinyService.TinyService")
plugin_manager.plug("plugins.sub_plugin.SubService.SubService")
plugin_manager.unplug()
