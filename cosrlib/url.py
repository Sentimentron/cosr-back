import urlparse
import urllib
import tldextract as _tldextract

# TODO init lazily
_tldextractor = _tldextract.TLDExtract(suffix_list_url=False)


class URL(object):
    """ Base class for manipulating an URL without context """

    def __init__(self, url, check_encoding=False):
        self.url = url

        if check_encoding:
            try:
                self.url.decode('ascii')
            except UnicodeDecodeError:
                p = urlparse.urlparse(self.url)

                # TODO: check the rightfulness of this!
                self.url = urlparse.urlunparse((
                    p[0],
                    p[1],
                    urllib.quote(p[2], safe="/"),
                    urllib.quote(p[3]),
                    urllib.quote(p[4], safe="&?="),
                    urllib.quote(p[5])
                ))

    def urljoin(self, href):
        """ Optimized version of urlparse.urljoin() """

        if href.startswith("http://") or href.startswith("https://"):
            return href
        elif href.startswith("/") and not href.startswith("//"):
            return self.homepage + href
        else:
            return urlparse.urljoin(self.url, href)

    # This is only called when the attribute is still missing
    def __getattr__(self, attr):
        # pylint: disable=redefined-variable-type

        if attr == "parsed":
            value = urlparse.urlparse(self.url)

        elif attr == "tldextracted":
            value = _tldextractor(self.url)

        elif attr == "normalized":
            value = urlparse.urlunparse((
                None,
                self.normalized_domain,
                self.parsed.path if self.parsed.path else "/",
                "",
                self.parsed.query,
                ""
            )).lstrip("/")

            if value.count("/") == 1:
                value = value.strip("/")

        elif attr == "normalized_without_query":
            value = urlparse.urlunparse((
                None,
                self.normalized_domain,
                self.parsed.path if self.parsed.path else "/",
                "",
                "",
                ""
            )).lstrip("/")

            if value.count("/") == 1:
                value = value.strip("/")

        elif attr == "homepage":
            value = urlparse.urlunparse((
                self.parsed.scheme,
                self.domain,
                "/",
                "",
                "",
                ""
            )).strip("/")

        # Pay-level domain
        elif attr == "pld":
            value = "%s.%s" % (self.tldextracted.domain, self.tldextracted.suffix)

        elif attr == "domain":
            value = self.parsed.netloc

        elif attr == "subdomain":
            value = self.tldextracted.subdomain

        elif attr == "normalized_domain":
            if self.domain.startswith("www."):
                value = self.domain[4:]
            else:
                value = self.domain
            if value.endswith(':80'):
                value = value[:-3]
            elif value.endswith(':443'):
                value = value[:-4]

        elif attr == "normalized_subdomain":
            if self.subdomain.startswith("www."):
                value = self.subdomain[4:]
            else:
                value = self.subdomain

        # https://en.wikipedia.org/wiki/Public_Suffix_List
        # Returns the domain name suffix ("co.uk" for "bbc.co.uk")
        elif attr == "suffix":
            value = self.tldextracted.suffix

        else:
            raise Exception("Unknown attribute!")

        self.__dict__[attr] = value
        return value
