meta:
  id: gns
  file-extension: gns
  endian: le
  encoding: ASCII

seq:
  - id: header
    type: gnsheader
  - id: posdata
    type: str
    size: header.datasize

types:
  gnsheader:
    seq:
      - id: magic
        contents: 'GNS'
        # size: 3
      - id: version
        type: u1
      - id: datasize
        type: u8le