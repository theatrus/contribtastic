//
//  ECUploadPayload.m
//  Contribtastic
//
//  Created by Yann Ramin on 12/1/11.
//  Copyright (c) 2011 StackFoundry LLC. All rights reserved.
//

#import "ECUploadPayload.h"

@implementation ECUploadPayload

@synthesize payloadDict = _payloadDict;

- (id) init {
	self = [super init];
	_payloadDict = [self buildPreamble];
	return self;
}

- (NSMutableDictionary*) buildPreamble {
	NSMutableDictionary *preamble = [[NSMutableDictionary alloc] init];
	[preamble setValue:@"orders" forKey:@"upload_type"];
	[preamble setValue:[NSNumber numberWithInt:1] forKey:@"version"];
	[preamble setValue:[NSDate date] forKey:@"generated_at"];
	return preamble;
}


@end
