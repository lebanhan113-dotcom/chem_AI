/* EduPlan AI 7.14 – shared bank online loader and directly visible update tile.
   Public fetch contains no answer key. Teacher imports are authenticated at server. */
(function(){'use strict';
let remoteCount=0,remoteError='';const el=id=>document.getElementById(id);
window.EduPlanBank={
 async loadRemote(){
  const seen=new Set(bank.map(q=>q.id));let next=0,total=0;
  try{for(let pass=0;pass<100;pass++){
   const r=await fetch('./api/public-bank?offset='+next,{cache:'no-store'});
   if(!r.ok)throw Error('HTTP '+r.status);
   const d=await r.json();const arr=Array.isArray(d.questions)?d.questions:[];
   for(const q of arr){if(!q||typeof q.id!=='string'||!q.stem||q.needs_review||seen.has(q.id))continue;
    if(![10,11,12].includes(Number(q.grade))||!['mcq','tf4','short','essay'].includes(q.kind))continue;
    const chapters=curriculum[String(q.grade)]||[];
    if(!chapters.some(ch=>ch.name===q.chapter&&ch.lessons.some(l=>l.name===q.lesson)))continue;
    seen.add(q.id);bank.push(q);if(typeof gradeCatalogSet!=='undefined')gradeCatalogSet.add(q.id);total++;
   }
   next+=arr.length;if(!d.hasMore||!arr.length)break;
  }remoteCount=total;remoteError='';return total;
  }catch(err){remoteError=err.message;console.warn('EduPlan cloud questions optional:',err.message);return total;}
 },
 get stats(){return {remoteCount,remoteError,total:bank.length};}
};
const previousDraw=draw;
draw=function(){if(app.tab==='bankupdate714')return `<section class="hero"><small>CẬP NHẬT NGÂN HÀNG · PHIÊN BẢN 7.14</small><h1>Bổ sung nguồn câu hỏi có kiểm soát</h1><p>Giáo viên cập nhật từ DOCX, CSV hoặc JSON. Học sinh chỉ nhận câu đã xác nhận và công bố qua máy chủ.</p></section><div class="grid"><section class="card"><h2>Giáo viên · Nhập câu hỏi</h2><ol><li>Chọn tệp Word, CSV hoặc JSON.</li><li>Hệ thống gợi ý lớp, chương, bài và phần I–IV.</li><li>Xem trước và sửa công thức/đáp án/lời giải.</li><li>Đánh dấu đã thẩm định từng câu.</li><li>Đồng bộ câu đủ điều kiện lên Supabase bằng khóa quản trị máy chủ.</li></ol><a class="btn primary" href="./teacher-tools/index.html">Mở công cụ cập nhật nguồn câu hỏi →</a><p class="help">Nếu máy chủ chưa cấu hình, thầy có thể lưu bản nháp và tải gói JSON riêng tư.</p></section><section class="card"><h2>Học sinh · Ngân hàng hiện có</h2><div class="stat-row"><span>Câu hỏi đã nạp trên thiết bị</span><b>${bank.length}</b></div><div class="stat-row"><span>Câu mới từ máy chủ trong lần tải trang</span><b>${remoteCount}</b></div><p class="help">Câu được công bố sẽ tự xuất hiện trong Kho câu, Luyện từng câu, Kiểm tra, Tạo đề và Phiếu học tập theo bài/chương/phần đang chọn.</p><button class="btn" onclick="navigate('bank')">Xem kho câu hỏi</button><button class="btn" onclick="navigate('practice')">Luyện 5/10/15 câu</button>${remoteError?'<p class="help">Máy chủ bổ sung chưa hoạt động. Ngân hàng gốc vẫn sử dụng bình thường.</p>':''}</section></div>`;return previousDraw();};
const previousMenu=paintMenu;
paintMenu=function(){previousMenu();const menu=el('menu');if(!menu)return;const html=`<section class="feature-group710 bankupdate-feature714"><div class="feature-heading710"><h3>Cập nhật nguồn ngân hàng câu hỏi</h3><p>Bổ sung đề Word theo khối → chương → bài → phần; câu phải được kiểm duyệt trước khi công bố.</p></div><div class="feature-grid710"><button class="feature710 ${app.tab==='bankupdate714'?'active':''}" onclick="navigate('bankupdate714')"><span class="feature-icon710" aria-hidden="true">⇪</span><span class="feature-text710"><strong>⇪ Cập nhật nguồn câu hỏi · DOCX/CSV/JSON</strong><small>Dành cho giáo viên · Rà soát trước khi đồng bộ online</small></span></button><button class="feature710" onclick="navigate('bank')"><span class="feature-icon710" aria-hidden="true">☷</span><span class="feature-text710"><strong>Ngân hàng đang sử dụng · ${bank.length} câu</strong><small>Lọc chương, bài, phần, mức độ và luyện ngay</small></span></button></div></section>`;
 menu.insertAdjacentHTML('afterbegin',html);if(app.tab==='bankupdate714')el('workspace-name').textContent='Cập nhật nguồn ngân hàng câu hỏi';
};
})();
