import React, {useEffect, useState} from 'react';
import {Img, cancelRender, continueRender, delayRender, staticFile} from 'remotion';

export const FX = (file: string) => staticFile('effects/' + file);

export const FontGate: React.FC<React.PropsWithChildren<{withSans?: boolean}>> = ({children, withSans = false}) => {
  const [handle] = useState(() => delayRender('Loading Vietnamese title fonts'));
  useEffect(() => {
    const fonts = [
      new FontFace('WeddingSerif', 'url(' + staticFile('fonts/CormorantGaramond.ttf') + ')'),
      new FontFace('WeddingSerif', 'url(' + staticFile('fonts/CormorantGaramond-Italic.ttf') + ')', {style: 'italic'}),
    ];
    if (withSans) {
      fonts.push(new FontFace('WeddingSans', 'url(' + staticFile('fonts/BeVietnamPro-Medium.ttf') + ')', {weight: '500'}));
    }
    Promise.all(fonts.map((font) => font.load())).then((loaded) => {
      loaded.forEach((font) => document.fonts.add(font));
      continueRender(handle);
    }).catch(cancelRender);
  }, [handle, withSans]);
  return children;
};

export const MediaImage: React.FC<{id: string; position?: string; className?: string}> = ({id, position, className}) =>
  <Img src={staticFile('photos/' + id + '.jpg')} className={className} style={{
    width: '100%', height: '100%', objectFit: 'cover', objectPosition: position ?? '50% 48%',
  }}/>;
