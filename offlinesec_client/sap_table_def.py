COLUMN_REPLACEMENT = {
    "RFCDES" : {
        "RFCDEST": ["RFC Destination", "Destination", "RFC-Destination"],
        "RFCTYPE": ["Connection Type", "Verbindungstyp"],
        "RFCOPTIONS": ["Options", "Optionen"],
        "RFCDOC1": ["Description", "Beschreibung"]
    },

    "UST04" : {
        "MANDT": ["Client", "Mandant", "Cl."],
        "BNAME": ["User", "Benutzername"],
        "PROFIL": ["Profile", "Profil"],
    },

    "USR02" : {
        "MANDT": ["Client", "Mandant", "Cl."],
        "BNAME": ["User Name", "Benutzername"],
        "GLTGB": [],
        "GLTGV": [],
        "USTYP": ["User Type", "Benutzertyp"],
        "UFLAG": ["User Lock Status", "Status der Benutzersperre"],
        "CLASS": ["User Master Maintenance: User Group", "Benutzerstammpflege: Benutzergruppe"],
    },

    "CWBNTCUST" : {
        "NUMM" : ["Note number", "Hinweisnummer"],
        "NTSTATUS" : ["Processing Status", "Proc. Status", "Bearb. Stat."],
        "PRSTATUS" : ["Implementation State", "Impl. State", "Einbaustand", "Impl. Status"],
        "IMPL_PROGRESS": ["Implementation Progress", "Impl."]
    },

    "CWBNTHEAD" : {
        "NUMM" : ["Note number", "Hinweisnummer"],
        "VERSNO": ["Version"],
        "INCOMPLETE": ["TRUE"]
    },

    "JAVA_SOFTS" : {
        "Version": [],
        "Vendor": [],
        "Name": [],
        "Location": []
    },

    "AGR_USERS": {
        "MANDT" : ["Client", "Mandant", "Cl."],
        "AGR_NAME": ["Role", "Rolle"],
        "UNAME": ["User Name", "Benutzername"],
        "FROM_DAT": ["Start date", "Beginndatum"],
        "TO_DAT": ["End date", "Enddatum"],

    },
    "AGR_1251": {
        "MANDT": ["Client", "Mandant", "Cl."],
        "AGR_NAME": ["Role", "Rolle"],
        "OBJECT": ["Object", "Objekt"],
        "AUTH": ["User Master Maint.: Authorization Name", "Benutzerstammpflege: Berechtigungsname"],
        "FIELD": ["Field name", "Feldname"],
        "LOW": ["Authorization value", "Berechtigungswert"],
        "HIGH": ["Authorization value", "Berechtigungswert"],
        "DELETED": ["ID whether object is deleted", "Kennzeichen, ob Objekt gelöscht"]
    },

    "RSPARAM": {
        "Parameter Name": ["Parametername"],
        "User-Defined Value": ["Benutzerdefinierter Wert"],
        "System Default Value": ["System-Defaultwert"],
        "System Default Value(Unsubstituted Form)": ["System-Defaultwert (Unsubst.Form)"],
        "Comment": ["Kommentar"]
    },
    "ICFSERVLOC": {
        "ICF_NAME": [],
        "ICFPARGUID": [],
        "ICFACTIVE": [],
    },
    "ICFSERVICE": {
        "ICF_NAME": [],
        "ICFPARGUID": [],
        "ICFNODGUID": [],
        "ICF_USER": [],
        "ICFALTNME": []
    },
}

DATA_REPLACEMENT = {
    "CWBNTCUST" : {
        "NTSTATUS" : {
            "A" : ["Finished","erledigt"],
            "N" : ["new", "neu"],
            "R" : ["Not Relevant", "nicht relevant"],
            "I" : ["In Process", "in Bearbeitung"]
        },
        "PRSTATUS" : {
            "N" : ["Can be implemented", "einbaubar"],
            "E" : ["Completely implemented", "vollständig eingebaut"],
            "O" : ["Obsolete", "obsolet"],
            "-" : ["Cannot be implemented", "nicht einbaubar"],
            ""  : ["Undefined Implementation State", "unbestimmter Einbauzustand"],
            "U" : ["Incompletely implemented", "unvollständig eingebaut"],
            "V" : ["Obsolete version implemented", "veraltete Version eingebaut"],
        },
    }
}