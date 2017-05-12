# Supported versions
#
# Title                               youversion      biblegateway
# English Standard Version (ESV)
# Amplified Bible (AMP)
# New Living Translation (NLT)
# The Message (MSG)
# The New Intenational Version (NIV)
# New Kings James Version (NKJV)

class Version():
    __versions = [
        {"title": "English Standard Version ({})".format, "letters": "ESV"},
        {"title": "Amplified Bible ({})".format, "letters": "AMP"},
        {"title": "New Living Translation ({})".format, "letters": "NLT"},
        {"title": "The Message ({})".format, "letters": "MSG"},
        {"title": "New Kings James Version ({})".format, "letters": "NKJV"},
        {"title": "New International Version ({})".format, "letters": "NIV"}
    ]

    def get_size(self):
        return len(self.__versions)

    def validate_version(self, letters):
        # for _version in self.__versions:
        #     if _version['letters'] is letters.upper():
        #         return True
        return letters in range(len(self.__versions))

    def get_all_versions_in_string(self):
        data = list()
        for x in range(len(self.__versions)):
            data.append(self.get_version_string(x))
        return data

    def get_version(self, index):
        if index < len(self.__versions):
            return self.__versions[index]
        raise Exception("Array index out of bounds")

    def get_version_string(self, index):
        v = self.get_version(index)
        letters = v['letters']
        return v['title'](letters)

    def get_version_letters(self, index):
        return self.get_version(index)['letters']


if __name__ == "__main__":
    # for testing
    v = Version()
    print(str(v.get_all_versions_in_string()))
    pass
