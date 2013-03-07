//
//  ECUploadManager.m
//  Contribtastic
//
//  Created by Yann Ramin on 12/1/11.
//  Copyright (c) 2011 StackFoundry LLC. All rights reserved.
//

#import "ECUploadManager.h"
#include "evecache/market.hpp"
#import "SCEvents.h"

@interface ECUploadManager () <SCEventListenerProtocol>
@property(nonatomic,retain) SCEvents *fsWatcher;
@end

@implementation ECUploadManager

@synthesize cacheDirectory = _cacheDirectory;
@synthesize lastValidCache = _lastValidCache;
@synthesize uploadQueue = _uploadQueue;
@synthesize fsWatcher = _fsWatcher;

- (void) locateCacheDirectory {
	
	NSError* error;
	
	NSString *hd = NSHomeDirectory();
	
	// Multiple EVE Clients would create their own Application Support folders
	// However, you can name the clients arbitrarily, so perhaps a more comprehensive search could be done
	// though that would be slow
	
	_cacheDirectory = [NSString stringWithFormat:@"%@/%@", hd, @"Library/Application Support/EVE Online/p_drive/Local Settings/Application Data/CCP/EVE/c_program_files_ccp_eve_tranquility/cache/MachoNet/87.237.38.200"];
	NSArray* contents = [[NSFileManager defaultManager] contentsOfDirectoryAtPath:_cacheDirectory error:&error];
	
	int max_ver = -1;
	
	for (NSString* name in contents) {
		if ([name intValue] > max_ver) {
			max_ver = [name intValue];
		}
	}
	
	NSString *tail = [NSString stringWithFormat:@"%d/%@", max_ver, @"CachedMethodCalls"];
	
	_cacheDirectory = [NSString stringWithFormat:@"%@/%@", _cacheDirectory, tail];
	
	NSLog(@"Using upload directory of %@", _cacheDirectory);
	
}

- (id) init {
	if(!(self = [super init]))
        return nil;
    
	[self locateCacheDirectory];
	_lastValidCache = [NSDate date]; // Set to now
	_uploadQueue = dispatch_queue_create("com.eve-central.upload_queue", NULL);
    
    // Watch for updates to the cache directory, and automatically do a scan after a change
    // has happened in it
    _fsWatcher = [SCEvents new];
    [_fsWatcher setDelegate:self];
    [_fsWatcher startWatchingPaths:[NSArray arrayWithObject:_cacheDirectory]];
    
    // Do an initial scan
    [self scan];
    
	return self;
}

- (void) dealloc {
	dispatch_release(_uploadQueue);
}

- (void) scanFile:(NSString*) name {
	EveCache::MarketParser *parser = new EveCache::MarketParser(std::string([name cStringUsingEncoding:[NSString defaultCStringEncoding]]));
	NSLog(@"Created parser for %@", name);
	if (!parser->valid()) {
		delete parser;
		return;
	}
	
	EveCache::MarketList ml = parser->getList();
	NSLog(@"Found valid cache file %@ for region %d type %d", name, ml.region(), ml.type());	
	
	const std::vector<EveCache::MarketOrder> buys = ml.getBuyOrders();
	const std::vector<EveCache::MarketOrder> sells = ml.getSellOrders();
	
	
	
	delete parser;
	
}

- (void) scan {
	// Scan runs in the uploadQueue
	dispatch_async(_uploadQueue, ^(void) {
		
		
		NSArray *files = [[NSFileManager defaultManager] contentsOfDirectoryAtPath:_cacheDirectory error:nil];
		
		NSDate *highestCache = _lastValidCache;
		
		for (NSString *jfile in files) {
			NSString *file = [NSString stringWithFormat:@"%@/%@", _cacheDirectory, jfile];
			
			NSDictionary *attr = [[NSFileManager defaultManager] attributesOfItemAtPath:file error:nil];

			NSDate* modDate = [attr valueForKey:NSFileModificationDate];

			if ([modDate compare:_lastValidCache] == NSOrderedDescending) {
				NSLog(@"File %@ is newer than the last scan", file);

				dispatch_async(_uploadQueue, ^(void) { [self scanFile:file]; });
			}
			
			if ([modDate compare:highestCache] == NSOrderedDescending) {
				highestCache = modDate; // Find the latest file
			}
		}
		
		dispatch_async(dispatch_get_main_queue(), ^(void) { 
			_lastValidCache = highestCache;
			// Avoid setting state outside of the main thread
		});
	});
}

- (void)pathWatcher:(SCEvents *)pathWatcher eventOccurred:(SCEvent *)event
{
    // Coalesce multiple file system events, in case a lot of changes are happening
    [NSObject cancelPreviousPerformRequestsWithTarget:self selector:@selector(scan) object:nil];
    [self performSelector:@selector(scan) withObject:nil afterDelay:0.5];
}


@end

