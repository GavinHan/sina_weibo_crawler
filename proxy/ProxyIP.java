import java.io.IOException;
import java.net.URISyntaxException;
import java.util.Vector;
import java.util.regex.Matcher;
import java.util.regex.Pattern;


import org.apache.http.client.ClientProtocolException;


public class ProxyIP {
    /**
     * There are proxy ips which haven't been verified on the page
     * like http://www.youdaili.cn/Daili/guonei/1843.html, use regex
     * to match all them out. 
     * @param a saved String html file
     * @return a String Vector contains all the IP on the html file
     * @throws ClientProtocolException
     * @throws IOException
     */
    public static Vector<String> getProxyIPs(String html) throws ClientProtocolException, IOException{
        Vector<String> IPs = new Vector<String>();
        Pattern p = Pattern.compile("\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}:\\d{1,5}");
        Matcher m = p.matcher(html);
        String s;
        String port;
        while(m.find()){
            s = m.group();
            port = s.split(":")[1];
            if(Integer.parseInt(port) < 65535){//The top range of the port number is 65535
                if(!IPs.contains(s)){
                    IPs.add(s);
                }
            }
            //System.out.println("找到一条ip "+s);
        }
        
        return IPs;
    }
    /**
     * Find all IP library links on the homepage of "http://www.youdaili.cn/".
     * @param a specified URL "http://www.youdaili.cn/"
     * @return a String Vector contains all URLs that contain some proxy IPs
     * @throws ClientProtocolException
     * @throws URISyntaxException
     * @throws IOException
     */
    public static Vector<String> getIPsPageLinks(String ipLibURL) throws ClientProtocolException, URISyntaxException, IOException{
        Vector<String> IPsPageLinks = new Vector<String>();     
        
        String html = new HTML().getHTML(ipLibURL)[1];
        Pattern p = Pattern.compile("(【国内】|【国外】).+?title");//"【国内】|【国外】).+?title"
        Matcher m = p.matcher(html);
        String s;
        while(m.find()){
            s = m.group();
            s = s.substring(s.indexOf("href")+6, s.indexOf("title")-2);
            IPsPageLinks.add(s);
            System.out.println("find ip library link: "+s);
        }
        
        return IPsPageLinks;
    }
    /**
     * Get all unverified proxy IP in all IP library links.
     * @param a specified URL "http://www.youdaili.cn/"
     * @return a String Vector contains all unverified IPs
     * @throws ClientProtocolException
     * @throws IOException
     * @throws URISyntaxException
     */
    public static Vector<String> getAllProxyIPs(String ipLibURL) throws ClientProtocolException, IOException, URISyntaxException{
        Vector<String> IPsPageLinks = getIPsPageLinks(ipLibURL);//"http://www.youdaili.cn/"
        Vector<String> onePageIPs = new Vector<String>();
        Vector<String> allIPs = new Vector<String>();
        for (int i = 0; i < IPsPageLinks.size(); i++) {
            String url = IPsPageLinks.get(i);
            String[] html = new HTML().getHTML(url);
            int page = 2;
            while(!html[0].equals("404")){
                //System.out.println("状态码 "+html[0]);
                System.out.println("start finding proxy IPs under this link: "+url);
                onePageIPs = getProxyIPs(html[1]);
                for(int j = 0; j < onePageIPs.size(); j++){
                    String s = onePageIPs.get(j);
                    if(!allIPs.contains(s)){
                        allIPs.add(s);
                    }
                }
                if(url.contains("_")){
                    url = url.substring(0,url.indexOf("_")+1) + page + ".html";
                }
                else{
                    url = url.substring(0,url.indexOf(".html"))+"_" +page+ ".html";
                }
                //System.out.println("page = "+page);
                html = new HTML().getHTML(url);
                //System.out.println("状态码 "+html[0]);
                page++;
            }
        }
        System.out.println("total proxy IP number:： "+allIPs.size());
        
        return allIPs;
    }
    /**
     * Test all proxy IPs and select the valid ones.
     * @param a String Vector which contains all proxy IPs
     * @return a String Vector which contains all valid IPs 
     * selected from all candidate proxy IPs
     * @throws ClientProtocolException
     * @throws IOException
     */
    public static Vector<String> getValidProxyIPs(Vector<String> allIPs) throws ClientProtocolException, IOException{
        System.out.println("********start getting valid proxy IPs********");
        
        Vector<String> validHostname = new Vector<String>();
        Vector<String> validIPs = new Vector<String>();
        int validIPNum = 0;
        for(int i = 0 ; i < allIPs.size(); i++){
            System.out.println("NO."+i+" ip be verified");
//          if(i == 100){
//              break;
//          }
            String ip = allIPs.get(i);
            String hostName = ip.split(":")[0];
            int port = Integer.parseInt(ip.split(":")[1]);
            String varifyURL = "http://iframe.ip138.com/ic.asp";//http://ip.uee.cn/ http://iframe.ip138.com/ic.asp
            
            String html = new HTML().getHTMLbyProxy(varifyURL, hostName, port);
            int iReconn = 0;
            while(html.equals("null")){//reconnect 2 times (total 3 times connection)
                if(iReconn == 2){
                    break;
                }
                html = new HTML().getHTMLbyProxy(varifyURL, hostName, port);
                iReconn++;
            }
            Pattern p = Pattern.compile("\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}");
            Matcher m = p.matcher(html);
            String s;
            if(m.find()){
                s = m.group();
                if(!validHostname.contains(s)){
                    validHostname.add(s);//
                    validIPs.add(s+":"+String.valueOf(port));
                    //bw.write(s+"\r\n");//write a valid proxy ip 
                    validIPNum++;
                    System.out.println("valid proxy IP "+ s+":"+String.valueOf(port));
                }
            }
            else{
                System.out.println("html doesn't contain an IP");}
        }
        System.out.println("total number of valid IPs "+validIPNum);
        
        return validIPs;
    }
    
    /**
     * Verify all valid IPs then save the "plain" IPs.
     * @param validIPs - the Vector<String> contains all valid IPs
     * @param plainPath - a String giving a path to save all "plain" IPs. "plain" IP indicate 
     * if it is used as a proxy IP to connect a weibo search page, the weibo sentence can be
     * read directly in the response HTML in a 2012 version but not enclosed as 
     * UTF8/GB2312/GBK charset format in 2014 version. I still do not know why it returns two 
     * versions HTML by different IPs. (2014/3/22)
     * @return
     * @throws ClientProtocolException
     * @throws IOException
     */
    public Vector<String> classifyIPs(Vector<String> validIPs, String plainPath) throws ClientProtocolException, IOException{
        final String verificationURL = "http://s.weibo.com/weibo/李雪山hakka&nodup=1&page=1";
        //Vector<String> utf8IPs = new Vector<String>();
        Vector<String> plainIPs = new Vector<String>();
        String ip;
        //int connectionTime = 0;
        for(int i = 0; i < validIPs.size(); i++){
            ip = validIPs.get(i);
            String html = new HTML().getHTMLbyProxy(verificationURL, ip.split(":")[0], Integer.parseInt(ip.split(":")[1]));
            int iReconn = 0;
            while(html.equals("null")){
                if(iReconn == 4){
                    break;
                }
                html = new HTML().getHTMLbyProxy(verificationURL, ip.split(":")[0], Integer.parseInt(ip.split(":")[1]));
                iReconn++;
                System.out.println("****"+ip+"is reconnecting the"+iReconn+" time****");
                
            }
                    if(html.contains("version=2012")){
                        plainIPs.add(ip);
                        System.out.println("plain: "+ip);
                        //write2txt(html, "d:/data/weibo/test/2012_"+i+".html");
                    }
            
        }
        
        return plainIPs;
    }
    
    public static void main(String[] args) throws ClientProtocolException, IOException, URISyntaxException, InterruptedException {
        long t1 = System.currentTimeMillis();
        
        String ipLibURL = "http://www.youdaili.cn/";
        Vector<String> validIPs = new Vector<String>();
        Vector<String> allIPs = new Vector<String>();
        Vector<String> plainIPs = new Vector<String>();
        allIPs = getAllProxyIPs(ipLibURL);
        FileOperation.write2txt(allIPs, "d:/data/weibo/allIPs.txt");
        validIPs = getValidProxyIPs(allIPs);
        FileOperation.write2txt(validIPs, "d:/data/weibo/validIPs.txt");
        plainIPs = new ProxyIP().classifyIPs(validIPs, "d:/data/weibo/plainIPs.txt");
        FileOperation.write2txt(plainIPs, "d:/data/weibo/plainIPs.txt");
        
        long t2 = System.currentTimeMillis();
        System.out.println((double)(t2 - t1)/60000 + "分钟");
    }
}
