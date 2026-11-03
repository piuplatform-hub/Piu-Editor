import React from 'react';
import {AbsoluteFill} from 'remotion';
import {FontGate,TextFx,FillFx} from './Film';

// Actual production components, compared against the same fully visible glyphs
// without a GSAP timeline. This gate targets the user's clipped-mark regression.
export const AccentRegression:React.FC<{reference:boolean}> = ({reference})=><AbsoluteFill style={{background:'#061b2b',fontFamily:'Be Vietnam Pro',color:'#f4f1e9'}}>
  <FontGate>
    <div style={{position:'absolute',left:100,top:70}}><TextFx lines={['TỰ TIN. TỪ KHỞI ĐẦU.']} size={100} still={reference}/></div>
    <div style={{position:'absolute',left:100,top:270}}><TextFx lines={['VỮNG KIẾN THỨC.']} size={100} accentLine={0} still={reference} effect="horizontal"/></div>
    <div style={{position:'absolute',left:100,top:470}}><TextFx lines={['HIỂU ĐÚNG.']} size={100} still={reference}/></div>
    <div style={{position:'absolute',left:100,top:670}}><TextFx lines={['RÈN TỪNG THAO TÁC.']} size={100} still={reference}/></div>
    <div style={{position:'absolute',left:100,top:870}}><FillFx text="SẴN SÀNG CẦM LÁI." size={100} still={reference}/></div>
    <div style={{position:'absolute',left:100,top:1070}}><TextFx lines={['Ă Ằ Ắ Ẳ Ẵ Ặ Â Ầ Ấ Ẩ Ẫ Ậ Ê Ề Ế Ể Ễ Ệ']} size={65} still={reference}/></div>
    <div style={{position:'absolute',left:100,top:1270}}><TextFx lines={['Ơ Ờ Ớ Ở Ỡ Ợ Ư Ừ Ứ Ử Ữ Ự Đ Ỳ Ý Ỷ Ỹ Ỵ']} size={65} still={reference}/></div>
  </FontGate>
</AbsoluteFill>;
