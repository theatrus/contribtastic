//
//  ECUploadManager.m
//  Contribtastic
//
//  Created by Yann Ramin on 12/1/11.
//  Copyright (c) 2011 StackFoundry LLC. All rights reserved.
//

#import "ECUploadManager.h"
#include "evecache/market.hpp"

@implementation ECUploadManager

@synthesize cacheDirectory = _cacheDirectory;
@synthesize lastValidCache = _lastValidCache;
@synthesize uploadQueue = _uploadQueue;

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
	self = [super init];
	[self locateCacheDirectory];
	_lastValidCache = [NSDate distantPast]; // Set to now
	_uploadQueue = dispatch_queue_create("com.eve-central.upload_queue", NULL);
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
	
	
	NSLog(@"Found valid cache file %@", name);
	
	
	delete parser;
	
}

- (void) scan {
	dispatch_async(dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0), ^(void) {
		
		
		NSArray *files = [[NSFileManager defaultManager] contentsOfDirectoryAtPath:_cacheDirectory error:nil];
		
		NSDate *highestCache = _lastValidCache;
		
		for (NSString *jfile in files) {
			NSString *file = [NSString stringWithFormat:@"%@/%@", _cacheDirectory, jfile];
			
			NSDictionary *attr = [[NSFileManager defaultManager] attributesOfItemAtPath:file error:nil];

			NSDate* modDate = [attr valueForKey:NSFileModificationDate];

			if ([modDate compare:_lastValidCache] == NSOrderedDescending) {
				NSLog(@"File %@ is newer than the last scan", file);

				dispatch_async(_uploadQueue, ^(void) { [self scanFile:file]; });
				// Process file
			}
			
			if ([modDate compare:highestCache] == NSOrderedDescending) {
				highestCache = modDate; // Find the latest file
			}
		}
		
		dispatch_async(dispatch_get_main_queue(), ^(void) { 
			_lastValidCache = highestCache;
		});
	});
}


@end

