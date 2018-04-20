from ._document import Document


class Invoice(Document):
    """an Invoice object contains image or pdf data of an invoice and is
    typically passed to :py:class:`~las.client.Client` for scanning.
    Supported file formats are jpeg, png, gif, bmp and pdf.

    :param str url: An http or https url pointing to an invoice image or pdf.
    :param str filename: A path to a local invoice image or pdf file.
    :param typing.BinaryIO fp: A file-like python object
    :param bytes content: Binary invoice image or pdf data.

    """
