import {put,get,list} from '@vercel/blob';

export async function read(path){const item=await get(path,{access:'private'});if(!item||item.statusCode!==200||!item.stream)return null;const str=await new Response(item.stream).text();return JSON.parse(str);}
export async function write(path,obj,overwrite=true){return put(path,JSON.stringify(obj),{access:'private',contentType:'application/json',addRandomSuffix:false,allowOverwrite:overwrite});}
export async function scan(prefix,max=500){let all=[],cursor;do{const page=await list({prefix,limit:100,cursor});for(const blob of page.blobs){if(!blob.pathname.endsWith('.json'))continue;const value=await read(blob.pathname);if(value)all.push(value);if(all.length>=max)break;}cursor=page.cursor;if(all.length>=max)break;}while(cursor);return all;}
