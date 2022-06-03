import danbi as di

conf = di.YAMLConfig(["res"])

print("----------------------------- getSignature -----------------------------")
print(conf.getSignatures(), "\n")

print("------------------------------ getConfig -------------------------------")
print(conf.getConfig("sql-test", 1.0), "\n")

print("--------------------------- get/set Current ----------------------------")
print(conf.setCurrent("common-config-test", 1.0).getCurrent(), "\n")

print("------------------------------- getValue -------------------------------")
print(conf.getValue("config.hosts[1].service"), "\n")

print("------------------------------- setValue -------------------------------")
print(conf.getValue("config.hosts[0].ip"))
conf.setValue("config.hosts[0].ip", "1.1.1.1")
print(conf.getValue("config.hosts[0].ip"), "\n")

print("------------------------------- persist --------------------------------")
conf.persist()

print(di.__version__)