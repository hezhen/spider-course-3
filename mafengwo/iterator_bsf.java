package cn.marble;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Queue;
import java.util.concurrent.ConcurrentLinkedQueue;

public class Main {

    Queue<String> currentQueue = new ConcurrentLinkedQueue<String>();

    Queue<String> childQueue = new ConcurrentLinkedQueue<String>();

    int currentLevel = 0;

    void appendDownloadedUrl(String url){

    }

    void appendErrorUrl(String url){

    }

    boolean isDownloaded(String url){

    }

    String getPageContent(String url) throws CrawlException, IOException {
        return "";
    }

    String savePageContent(String pageContent){
        return "";
    }

    void enqueueUrls(ConcurrentLinkedQueue<String> urls){
        childQueue.addAll(urls);
    }

    void enqueueUrlsFromPageSrc(String pageContent){

    }

    void enqueueUrl(String url){
        childQueue.add(url);
    }

    String dequeueUrl(){
        String url = currentQueue.poll();
        if ( url == null ){
            currentLevel ++;
            if ( currentLevel == HEIGHT )
                return null;
            currentQueue = childQueue;
            childQueue = new ConcurrentLinkedQueue<String>();
            url = currentQueue.poll();
        }
        return url;
    }

    String rootNode;

    final static int WIDTH = 50;
    final static int HEIGHT = 5;

    void crawl(String url){
        String pageContent;
        try{
            pageContent = getPageContent(url);
            savePageContent(pageContent);
        } catch( Exception e ){
            appendErrorUrl(url);
            return;
        }

        enqueueUrlsFromPageSrc(pageContent);
    }

    void start(){

        int curLevel = 0;
        enqueueUrl("http://www.mafengwo.cn");

        while( true ){
            String url = dequeueUrl();
            if ( url == null ){
                if ( url == null )
                    break;
            }
            crawl(url);

        }
    }

    public static void main(String[] args) {
	// write your code here
    }
}
