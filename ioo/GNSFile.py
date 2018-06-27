# -*- coding: utf-8 -*-

class GNS:

    @staticmethod
    def save(graphNodeViewScene):
        nodes = []

        from controls.GraphicsView.GraphNodeView import GraphNodeViewScene
        from controls.GraphicsView.GraphNodeView import GraphNodeItem
        pos = []
        for gItem in graphNodeViewScene.items():
            pos.append((
                (gItem.pos().x(), gItem.pos().y()),
                gItem.rotation(), gItem.scale()
            ))

        import sys
        import json
        from io import BytesIO
        import ioo.BinaryWriter as BinaryWriter
        with open('Scene.gns', 'wb') as f:
            stream = BytesIO()
            writer = BinaryWriter.BinaryWriter(stream)
            writer.WriteBytes(b'GNS')
            writer.WriteByte(b'\x01')
            posData = json.dumps(pos).encode()
            writer.WriteUInt64(len(posData))
            writer.WriteBytes(posData)

            print('writeDataSize: ', len(posData))

            f.write(stream.getbuffer())
            f.close()


    @staticmethod
    def load():
        import sys
        import ioo.BinaryReader as BinaryReader
        from io import BytesIO
        import json
        import kaitaistruct

        with open('Scene.gns', 'rb') as f:
            from ioo import gns
            gnsData = gns.Gns(kaitaistruct.KaitaiStream(BytesIO(f.read())))
            print(json.loads(gnsData.posdata))

            f.close()



if __name__ == '__main__':

    with open('Scene.gns', 'wb') as f:

        stream = BinaryWriter()
        stream.add_sign('GNS')
        stream.add_float(1.0)
        # stream += time.time()

        f.write(stream.serial())
        f.close()