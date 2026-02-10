EXCLUDE_PARAMS =["FN_BDCALTLOG", "FN_BDCLOG", "FN_EXTRACT", "SAPARGV", "SAPGLOBALHOST", "SAPLOCALHOST",
               "SAPLOCALHOSTFULL", "SAPPROFILE", "SAPPROFILE_IN_EFFECT", "SAPSYSTEMNAME", "SETENV_.*", "Execute_.*",
               "Start_Program_.*", r"_\S{2}", "dbs/hdb/schema", "dbs/mss/dbname", "dbs/ora/tnsname", "dbs/syb/dbname",
               "enq/server/schema_0", "enque/encni/hostname", "enque/serverhost", "igs/listener/rfc", "igs/mux/ip",
               "ms/comment", "rdisp/j2ee_profile", "rdisp/j2ee_profile", "rdisp/mshost", "rdisp/msserv", "rdisp/myname",
               "rlfw/bri/msserv", "rlfw/upg/msserv", "snc/gssapi_lib", "snc/identity/as", "vmcj/debug_proxy/cfg/msHost",
               "vmcj/debug_proxy/cfg/msPort","CPU_CORES", "EM/TOTAL_SIZE_MB","ztta/.*","abap/.*","dbs/.*","em/.*","zcsa/.*",
               "stat/.*","rspo/.*", "ipc/.*", "is/.*","rsdb/.*","igs/.*","enq/.*","rdisp/wp.*","__SAPPROFILE_.*"
               ]